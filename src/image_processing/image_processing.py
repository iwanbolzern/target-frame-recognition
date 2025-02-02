import cv2
import numpy as np

from src.image_processing import Contour
from src.image_processing import Generic
# load the image
from src.image_processing import ProportionHandler
from src.image_processing import Tree


class ImageProcessing:

    def __init__(self):
        self.min_max_contours = Generic(min=3, max=3)
        self.grey_scale_image = None
        self.black_white_image = None
        self.processed_image = None

        # start livestream
        #self.live_stream = LiveStream()
        #self.live_stream.start()

    def to_binary_img(self, image):
        self.grey_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.adaptiveThreshold(self.grey_scale_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                       cv2.THRESH_BINARY, 101, 7)

    def process_image(self, image):
        # Debug raw image
        #cv2.imshow('Orginal image', image)
        #cv2.waitKey(1)
        # end debug

        # convert the image to grayscale, blur it
        # Debug
        self.processed_image = image.copy()
        # end Debug
        self.grey_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.black_white_image = cv2.adaptiveThreshold(self.grey_scale_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 7)

        # find contours
        # get all contours which are nested into each other. hierarchy  [Next, Previous, First_Child, Parent]
        (im2, contours, hierarchy) = cv2.findContours(self.black_white_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [Contour(contour) for contour in contours]
        # Debug
        #self.processed_image = image.copy()
        #for c in contours:
        #    cv2.drawContours(self.processed_image, [c.points], -1, (0, 255, 0), 3)
        #cv2.imshow("All contours Image", self.processed_image)
        #cv2.waitKey(1)
        # end Debug

        possible_contours = self.get_possible_contours(contours, hierarchy)

        proportion_handler = ProportionHandler(2)
        for contours in possible_contours:
            # Debug
            #self.processed_image = image.copy()
            #for c in contours:
            #    cv2.drawContours(self.processed_image, [c.points], -1, (0, 255, 0), 3)
            #cv2.imshow("Processed Image", self.processed_image)
            #cv2.waitKey(1)
            # end Debug

            satisfy = proportion_handler.does_contours_satisfy_proportions(contours)
            if satisfy:
                # calc and draw point
                x = [contour.center[0] for contour in contours]
                y = [contour.center[1] for contour in contours]
                centroid = (int(sum(x) / len(contours)), int(sum(y) / len(contours)))

                # Debug
                #cv2.circle(self.processed_image, centroid, 3, (255, 0, 0), thickness=1, lineType=8, shift=0)
                #for c in contours:
                #    cv2.drawContours(self.processed_image, [c.points], -1, (0, 255, 0), 3)
                #    cv2.circle(self.processed_image, c.center, 3, (0, 0, 255), thickness=1, lineType=8, shift=0)

                #cv2.imshow("Processed Image", self.processed_image)
                #cv2.waitKey(1)
                # End Debug

                return True, centroid

        # Debug
        #for contours in possible_contours:
        #    self.processed_image = image.copy()
        #    for c in contours:
        #        cv2.drawContours(self.processed_image, [c.points], -1, (0, 255, 0), 3)
        #    cv2.imshow("Processed Image", self.processed_image)
        #    cv2.waitKey(1)
        # end Debug

        #self.live_stream.send_frame(self._create_debug_window())
        return False, None

    def check_for_for_corners(self):
        # approximate the contour
        #peri = cv2.arcLength(contour, True)
        #approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # if our approximated contour has four points
        #if len(approx) == 4:
        pass

    def get_possible_contours(self, cntrs, hierarchy):
        if hierarchy is None:
            return []

        tree = Tree(hierarchy)
        possible_contours = []
        for leave in tree.leaves:
            parents, has_more = leave.get_n_parents(self.min_max_contours.max)
            if len(parents) >= self.min_max_contours.min: # check if there are enough contours in each other
                possible_contours.append([cntrs[leave.index]] + [cntrs[parent.index] for parent in parents])

                # check if there are more contours in each other
                cur_leave = leave
                while has_more:
                    cur_leave = cur_leave.parent
                    parents, has_more = cur_leave.get_n_parents(self.min_max_contours.max)
                    possible_contours.append([cntrs[cur_leave.index]] + [cntrs[parent.index] for parent in parents])

        return possible_contours

    def show_all_images(self):
        tmp_img = self._create_debug_window()
        #cv2.imshow("Debug Window", cv2.resize(tmp_img, (1200, 800)))

        # cv2.imshow('Grey Scale Image', self.grey_scale_image)
        # cv2.imshow('Grey Blur Image', self.grey_blur_image)
        # cv2.imshow('Black White Image', self.black_white_image)
        # cv2.imshow('Edged Image', self.edged_image)
        cv2.imshow('Prozessed Image', self.processed_image)

    def _create_debug_window(self):
        tmp_img_row1 = np.concatenate((cv2.cvtColor(self.grey_scale_image, cv2.COLOR_GRAY2RGB),
                                       cv2.cvtColor(self.black_white_image, cv2.COLOR_GRAY2RGB)), axis=1)
        tmp_img_row2 = self.processed_image

        new_shape = tmp_img_row1.shape
        shape_diff = np.array(new_shape) - np.array(tmp_img_row2.shape)
        tmp_img_row2 = np.lib.pad(tmp_img_row2, ((0, shape_diff[0]), (0, shape_diff[1]), (0, shape_diff[2])),
                                  'constant', constant_values=(0))

        return np.concatenate((tmp_img_row1, tmp_img_row2), axis=0)
