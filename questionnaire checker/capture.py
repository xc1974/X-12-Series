import cv2

def capture_image(output_path="questionnaire.jpg"):
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        cv2.imshow('Press SPACE to capture', frame)
        
        if cv2.waitKey(1) & 0xFF == ord(' '):
            cv2.imwrite(output_path, frame)
            break
    
    cap.release()
    cv2.destroyAllWindows()

capture_image()