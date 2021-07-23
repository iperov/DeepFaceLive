import numpy as np

def nms(x1, y1, x2, y2, scores, thresh):
    """
    Non-Maximum Suppression

        x1,y1,x2,y2,scores  np.ndarray of box coords with the same length

    returns indexes of boxes
    """
    keep = []
    if len(x1) == 0:
        return keep

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx_1, yy_1 = np.maximum(x1[i], x1[order[1:]]), np.maximum(y1[i], y1[order[1:]])
        xx_2, yy_2 = np.minimum(x2[i], x2[order[1:]]), np.minimum(y2[i], y2[order[1:]])

        width, height = np.maximum(0.0, xx_2 - xx_1 + 1), np.maximum(0.0, yy_2 - yy_1 + 1)
        ovr = width * height / (areas[i] + areas[order[1:]] - width * height)

        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1]
    return keep