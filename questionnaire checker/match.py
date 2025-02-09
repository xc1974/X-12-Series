def map_boxes_to_template(boxes, image_shape):
    # 按坐標排序（假設從上到下排列問題）
    boxes.sort(key=lambda b: (b[1], b[0]))
    
    # 假設每個問題有4個選項（需根據實際模板調整）
    questions = []
    row_y = None
    current_row = []
    
    for box in boxes:
        x, y, w, h = box
        if row_y is None or abs(y - row_y) < 20:  # 同一行
            current_row.append(box)
        else:
            # 按列排序並添加到問題
            current_row.sort(key=lambda b: b[0])
            questions.append(current_row)
            current_row = [box]
        row_y = y
    
    return questions