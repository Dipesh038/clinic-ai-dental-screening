PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def strip_exif_metadata(file_bytes: bytes, content_type: str) -> bytes:
    if content_type == "image/jpeg":
        return _strip_jpeg_exif(file_bytes)
    if content_type == "image/png":
        return _strip_png_exif(file_bytes)
    return file_bytes


def _strip_jpeg_exif(file_bytes: bytes) -> bytes:
    if not file_bytes.startswith(b"\xff\xd8"):
        return file_bytes

    output = bytearray(file_bytes[:2])
    index = 2
    length = len(file_bytes)

    while index + 4 <= length and file_bytes[index] == 0xFF:
        marker = file_bytes[index + 1]
        if marker == 0xDA:
            output.extend(file_bytes[index:])
            return bytes(output)

        segment_length = int.from_bytes(file_bytes[index + 2 : index + 4], "big")
        segment_end = index + 2 + segment_length
        if segment_length < 2 or segment_end > length:
            return file_bytes

        segment = file_bytes[index:segment_end]
        payload = file_bytes[index + 4 : segment_end]
        is_exif_segment = marker == 0xE1 and payload.startswith(b"Exif\x00\x00")
        if not is_exif_segment:
            output.extend(segment)

        index = segment_end

    output.extend(file_bytes[index:])
    return bytes(output)


def _strip_png_exif(file_bytes: bytes) -> bytes:
    if not file_bytes.startswith(PNG_SIGNATURE):
        return file_bytes

    output = bytearray(PNG_SIGNATURE)
    index = len(PNG_SIGNATURE)
    length = len(file_bytes)

    while index + 12 <= length:
        chunk_length = int.from_bytes(file_bytes[index : index + 4], "big")
        chunk_type = file_bytes[index + 4 : index + 8]
        chunk_end = index + 12 + chunk_length
        if chunk_end > length:
            return file_bytes

        if chunk_type != b"eXIf":
            output.extend(file_bytes[index:chunk_end])

        index = chunk_end

    output.extend(file_bytes[index:])
    return bytes(output)
