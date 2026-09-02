#!/usr/bin/env python3

import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import iradon


DB_PATH = Path("scan.sqlite")


# ============================================================
# 1. Đọc dữ liệu từ SQLite
# ============================================================

with sqlite3.connect(DB_PATH) as connection:
    rows = connection.execute(
        """
        SELECT angle_degrees, detector_count, light_values
        FROM projections
        ORDER BY angle_degrees
        """
    ).fetchall()


if not rows:
    raise RuntimeError("Bảng projections không có dữ liệu")


angles = np.array(
    [angle for angle, _, _ in rows],
    dtype=np.float64,
)

detector_counts = {
    angle: detector_count
    for angle, detector_count, _ in rows
}

projections = []


# ============================================================
# 2. Chuyển chuỗi JSON thành mảng NumPy
# ============================================================

for angle, declared_count, light_values_text in rows:
    values = np.asarray(
        json.loads(light_values_text),
        dtype=np.float64,
    )

    if values.size != declared_count:
        raise ValueError(
            f"Góc {angle}: detector_count={declared_count}, "
            f"nhưng thực tế có {values.size} giá trị"
        )

    projections.append(values)


print(f"[+] Số phép chiếu: {len(projections)}")
print(f"[+] Góc: {angles.min()}° → {angles.max()}°")
print(
    f"[+] Detector: "
    f"{min(map(len, projections))} → "
    f"{max(map(len, projections))}"
)


# ============================================================
# 3. Căn giữa và padding các phép chiếu
# ============================================================

# Mỗi góc có detector_count khác nhau.
# Vì vậy phải đệm các mảng về cùng độ dài.
max_detectors = max(map(len, projections))

# iradon yêu cầu:
# hàng = vị trí detector
# cột = góc chiếu
sinogram = np.zeros(
    (max_detectors, len(projections)),
    dtype=np.float64,
)

for column, values in enumerate(projections):
    padding = max_detectors - values.size
    start = padding // 2

    sinogram[
        start:start + values.size,
        column
    ] = values


print(f"[+] Kích thước sinogram: {sinogram.shape}")


# Lưu sinogram để kiểm tra
plt.figure(figsize=(10, 7))

plt.imshow(
    sinogram,
    cmap="gray",
    aspect="auto",
    extent=[
        angles.min(),
        angles.max(),
        max_detectors,
        0,
    ],
)

plt.xlabel("Góc chiếu")
plt.ylabel("Vị trí detector")
plt.title("Sinogram")

plt.tight_layout()
plt.savefig("sinogram.png", dpi=200)
plt.close()


# ============================================================
# 4. Inverse Radon transform
# ============================================================

reconstructed = iradon(
    sinogram,
    theta=angles,
    filter_name="ramp",
    circle=False,

    # Nếu không đặt output_size, scikit-image sẽ tạo ảnh nhỏ
    # và có thể cắt mất phần chữ ở hai bên.
    output_size=max_detectors,
)


# Dữ liệu của bài cho ảnh bị ngược theo chiều dọc
reconstructed = np.flipud(reconstructed)


plt.imsave(
    "reconstructed_full.png",
    reconstructed,
    cmap="gray",
)


# ============================================================
# 5. Crop về kích thước ảnh gốc
# ============================================================

# Góc 0° tương ứng với chiều rộng ảnh gốc
crop_width = detector_counts.get(
    0,
    max_detectors,
)

# Góc 90° tương ứng với chiều cao ảnh gốc
crop_height = detector_counts.get(
    90,
    max_detectors,
)

height, width = reconstructed.shape

x0 = max(
    0,
    (width - crop_width) // 2,
)

y0 = max(
    0,
    (height - crop_height) // 2,
)

cropped = reconstructed[
    y0:min(height, y0 + crop_height),
    x0:min(width, x0 + crop_width),
]


# ============================================================
# 6. Tăng tương phản
# ============================================================

low, high = np.percentile(
    cropped,
    [1, 99.8],
)

if high > low:
    cropped = (cropped - low) / (high - low)
    cropped = np.clip(cropped, 0, 1)


plt.imsave(
    "reconstructed_crop.png",
    cropped,
    cmap="gray",
)


print("[+] Đã tạo sinogram.png")
print("[+] Đã tạo reconstructed_full.png")
print("[+] Đã tạo reconstructed_crop.png")
