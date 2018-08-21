import scipy.misc
import cv2

class WritePlate():
    def __init__(self):
        pass

    def __call__(self, path_to_image = '', region = None, plate = ''):
        if plate != 'NOPLATE':
            path_to_new_image = path_to_image[:path_to_image.rfind('.')]

            px0 = region[0]['x']
            py0 = region[0]['y']
            px1 = region[2]['x']
            py1 = region[2]['y']

            textx = region[0]['x']
            texty = region[0]['y']


            img = cv2.imread(path_to_image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.rectangle(img,(px0,py0),(px1,py1),(0,255,0),3)

            img = cv2.putText(img, plate,
                              (textx, int(texty*0.95)),
                              cv2.FONT_HERSHEY_SIMPLEX,
                              1,
                              (0,255,3),
                              2,
                              cv2.LINE_AA)
            save_in = "{}_plate.jpg".format(path_to_new_image)
            scipy.misc.imsave(save_in, img)

            return save_in

        else:
            path_to_new_image = path_to_image[:path_to_image.rfind('.')]

            img = cv2.imread(path_to_image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            save_in = "{}_plate.jpg".format(path_to_new_image)
            scipy.misc.imsave(save_in, img)

            return save_in


if __name__ == '__main__':

    info = {'path': '/home/stanlee321/2018-02-06_10-31-56/2018-02-06_10-31-56_2wm_cropped.jpg',
             'plate': {'matches_template': 0, 'plate': '2073EX1', 'confidence': 88.61466979980469},
             'box': [{'y': 290, 'x': 154}, {'y': 298, 'x': 254}, {'y': 341, 'x': 249}, {'y': 333, 'x': 151}
             ]}
    path = info['path']
    region = info['box']
    plate = info['plate']
    write = WritePlate()
    response = write(path, region, plate)
    print(response)