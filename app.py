import streamlit as st
from PIL import Image
import io, zipfile, time

st.set_page_config(page_title="Smart Image Compressor", page_icon="🗜️", layout="centered")
st.title("🗜️ Smart Image Compressor")
st.write("Upload multiple images and compress them efficiently. Sizes are shown in **KB**.")

quality = st.slider("Compression Quality (Lower = Smaller File)", 10, 95, 70)
uploaded_files = st.file_uploader(
    "Drag & Drop Images or Click to Upload",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

MAX_TOTAL_KB = 200_000  # ≈200 MB safety limit

def compress_image(file, quality_value):
    """Compress a single image and return BytesIO buffer."""
    image = Image.open(file)
    fmt = image.format if image.format else "JPEG"
    buffer = io.BytesIO()
    image.save(buffer, format=fmt, optimize=True, quality=quality_value)
    buffer.seek(0)
    return buffer

if uploaded_files:
    total_size_kb = sum(len(f.getbuffer()) for f in uploaded_files) / 1024
    if total_size_kb > MAX_TOTAL_KB:
        st.error(f"❌ Total upload size {total_size_kb/1024:.2f} MB exceeds 200 MB limit. "
                 "Please upload fewer or smaller images.")
        st.stop()

    total_files = len(uploaded_files)
    st.info(f"Processing {total_files} image(s)... please wait.")
    progress = st.progress(0)
    status = st.empty()

    zip_buffer = io.BytesIO()
    total_orig_kb, total_comp_kb = 0, 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, file in enumerate(uploaded_files, start=1):
            status.markdown(f"**Compressing {i}/{total_files}: `{file.name}`**")
            orig_kb = len(file.getbuffer()) / 1024
            total_orig_kb += orig_kb

            comp_buf = compress_image(file, quality)
            comp_kb = len(comp_buf.getvalue()) / 1024
            total_comp_kb += comp_kb

            zipf.writestr(file.name, comp_buf.getvalue())
            # free memory from current image
            comp_buf.close()
            file.close()

            percent = int(i / total_files * 100)
            progress.progress(percent / 100)
            time.sleep(0.01)

    progress.progress(1.0)
    status.text("✅ Processing complete (100%)")

    zip_buffer.seek(0)
    st.success(f"✅ Compressed {total_files} images successfully!")
    st.write(f"**Total Original Size:** {total_orig_kb:.1f} KB")
    st.write(f"**Total Compressed Size:** {total_comp_kb:.1f} KB")
    st.write(f"**Space Saved:** {(1 - total_comp_kb/total_orig_kb)*100:.1f}%")

    st.download_button(
        label="⬇️ Download All as ZIP",
        data=zip_buffer,
        file_name="compressed_images.zip",
        mime="application/zip"
    )
