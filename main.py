import cv2
import os
import glob
import ultralytics
from ultralytics import YOLO


def process_image(model, image_path, output_path):
    # 进行预测
    results = model.predict(source=image_path)

    # 提取第一个结果的原始图像和预测框
    result = results[0]
    image = result.orig_img

    # 画出预测结果
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        label = result.names[int(box.cls)]
        confidence = box.conf[0]

        # 画出框和标签
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(image, f'{label} {confidence:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (36, 255, 12), 2)

    # 保存结果图像
    cv2.imwrite(output_path, image)
    print(f'Results saved to {output_path}')


def process_video(model, video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(source=frame)
        result = results[0]
        frame = result.orig_img

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            label = result.names[int(box.cls)]
            confidence = box.conf[0]

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'{label} {confidence:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (36, 255, 12), 2)

        out.write(frame)

    cap.release()
    out.release()
    print(f'Results saved to {output_path}')


def main():
    # 定义模型路径和输入文件夹路径
    model_path = 'runs/detect/train5/weights/best.pt'
    input_folder = 'D:/LT/YOLOv8_cs-main/vides'
    output_folder = 'results'

    # 加载模型
    model = YOLO(model_path)

    # 确保结果文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 处理所有图像文件
    image_extensions = ['jpg', 'jpeg', 'png']
    for ext in image_extensions:
        for image_path in glob.glob(os.path.join(input_folder, f'*.{ext}')):
            output_path = os.path.join(output_folder, os.path.basename(image_path))
            process_image(model, image_path, output_path)

    # 处理所有视频文件
    video_extensions = ['mp4', 'avi', 'mov']
    for ext in video_extensions:
        for video_path in glob.glob(os.path.join(input_folder, f'*.{ext}')):
            output_path = os.path.join(output_folder, os.path.basename(video_path))
            process_video(model, video_path, output_path)


if __name__ == "__main__":
    main()
