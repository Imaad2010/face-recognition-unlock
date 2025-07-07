# face-recognition-unlock
A Jetson Nano-based smart unlock system using face recognition and UDP broadcasting.
# 🔓 Face Recognition Unlock System using Jetson Nano

This project is a real-time face recognition–based smart unlocking system using **Jetson Nano**, **OpenCV**, **UDP broadcasting**, and **Text-to-Speech (TTS)**. The system can be used to unlock doors or gates wirelessly when an authorized face is detected.

---

## 🎯 What It Does

- Detects known faces using a connected camera (real-time)
- Requires the face to stay in view for at least **2 seconds** to confirm
- Announces the person’s name and confidence via speaker
- Sends a **UDP broadcast** to trigger an external gate or door unlock
- Logs every unlock attempt with timestamps

---

## 🧠 Technologies Used

- Python
- OpenCV (`cv2`)
- face_recognition
- pyttsx3 (Text-to-Speech)
- UDP Sockets
- Jetson Nano (hardware platform)

---

## 📂 File Structure

| File           | Description                                |
|----------------|--------------------------------------------|
| `main.py`      | Main face recognition + unlock script      |
| `requirements.txt` | List of required Python libraries     |
| `recognition_log.txt` | Logs recognized faces with timestamp |

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Imaad2010/face-recognition-unlock.git
cd face-recognition-unlock
