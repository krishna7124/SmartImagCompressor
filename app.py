import streamlit as st
from PIL import Image
import io
import zipfile
import time

st.set_page_config(page_title="Smart Image Compressor", page_icon="🗜️", layout="centered")

st.title("🗜️ Smart Image Compressor")
st.write("Upload single or multiple high-quality images and compress them efficiently. File sizes are shown in **KB**.")

# --- User Inputs ---
quality = st.slider("Select Compression Quality (Lower = Smaller File)", 10, 95, 70)
uploaded_files = st.file_uploader(
    "Drag & Drop Images or Click to Upload",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# --- Function to Compress an Image ---
def compress_image(file, quality_value):
    image = Image.open(file)
    img_format = image.format if image.format else "JPEG"
    buffer = io.BytesIO()
    image.save(buffer, format=img_format, optimize=True, quality=quality_value)
    buffer.seek(0)
    return buffer

# --- Main Processing ---
if uploaded_files:
    st.info(f"Uploaded {len(uploaded_files)} image(s). Processing started...")
    progress_bar = st.progress(0)
    progress_text = st.empty()
    current_status = st.empty()

    compressed_files = []
    total_orig_kb, total_comp_kb = 0, 0
    total_files = len(uploaded_files)

    for idx, file in enumerate(uploaded_files):
        current_file_num = idx + 1
        current_status.markdown(f"**Processing image {current_file_num}/{total_files}: `{file.name}`**")

        # Compress image
        orig_kb = len(file.getbuffer()) / 1024
        total_orig_kb += orig_kb
        buffer = compress_image(file, quality)
        comp_kb = len(buffer.getvalue()) / 1024
        total_comp_kb += comp_kb

        compressed_files.append({
            "name": file.name,
            "buffer": buffer,
            "orig_kb": orig_kb,
            "comp_kb": comp_kb
        })

        # Update progress
        progress_percent = int((current_file_num / total_files) * 100)
        progress_bar.progress(progress_percent / 100)
        progress_text.text(f"Progress: {progress_percent}% complete")

        # Add small delay for smoothness (optional)
        time.sleep(0.05)

    progress_text.text("✅ Processing complete (100%)")
    current_status.empty()
    progress_bar.empty()

    # --- Single File Case ---
    if len(compressed_files) == 1:
        file = compressed_files[0]
        st.success(f"✅ Compressed: {file['name']}")
        st.write(f"**Original:** {file['orig_kb']:.1f} KB → **Compressed:** {file['comp_kb']:.1f} KB "
                 f"(**Saved:** {(1 - file['comp_kb']/file['orig_kb'])*100:.1f}%**)")
        st.download_button(
            label="⬇️ Download Compressed Image",
            data=file["buffer"],
            file_name=f"compressed_{file['name']}",
            mime="image/jpeg"
        )

    # --- Multiple Files Case ---
    else:
        st.success(f"✅ Compressed {len(compressed_files)} images successfully!")
        st.write(f"**Total Original Size:** {total_orig_kb:.1f} KB")
        st.write(f"**Total Compressed Size:** {total_comp_kb:.1f} KB")
        st.write(f"**Space Saved:** {(1 - total_comp_kb/total_orig_kb)*100:.1f}%")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in compressed_files:
                zipf.writestr(file["name"], file["buffer"].getvalue())
        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download All as ZIP",
            data=zip_buffer,
            file_name="compressed_images.zip",
            mime="application/zip"
        )
