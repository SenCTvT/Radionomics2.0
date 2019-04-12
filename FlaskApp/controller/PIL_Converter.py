from PIL import Image
import numpy as np
import pydicom as dicom

#Source: https://github.com/darcymason/pydicom/blob/master/pydicom/contrib/pydicom_PIL.py
#Credit: Krishanu

class PILConverter:
    @classmethod
    def get_LUT_value(cls, data, window, level):
        return np.piecewise(data,
                            [data <= (level - 0.5 - (window - 1) / 2),
                             data > (level - 0.5 + (window - 1) / 2)],
                            [0, 255, lambda data: ((data - (level - 0.5)) /
                             (window - 1) + 0.5) * (255 - 0)])

    @classmethod
    def get_PIL_image(cls, dataset):
        if ('PixelData' not in dataset):
            raise TypeError("Cannot show image -- DICOM dataset does not have "
                            "pixel data")
        # can only apply LUT if these window info exists
        if ('WindowWidth' not in dataset) or ('WindowCenter' not in dataset):
            bits = dataset.BitsAllocated
            samples = dataset.SamplesPerPixel
            if bits == 8 and samples == 1:
                mode = "L"
            elif bits == 8 and samples == 3:
                mode = "RGB"
            elif bits == 16:
                # not sure about this -- PIL source says is 'experimental'
                # and no documentation. Also, should bytes swap depending
                # on endian of file and system??
                mode = "I;16"
            else:
                raise TypeError("Don't know PIL mode for %d BitsAllocated "
                                "and %d SamplesPerPixel" % (bits, samples))

            # PIL size = (width, height)
            size = (dataset.Columns, dataset.Rows)

            # Recommended to specify all details
            # by http://www.pythonware.com/library/pil/handbook/image.htm
            im = Image.frombuffer(mode, size, dataset.PixelData,
                                      "raw", mode, 0, 1)

        else:
            image = cls.get_LUT_value(dataset.pixel_array, dataset.WindowWidth,dataset.WindowCenter)
            # Convert mode to L since LUT has only 256 values:
            #   http://www.pythonware.com/library/pil/handbook/image.htm
            im = Image.fromarray(image).convert('L')

        return im

if __name__ == '__main__':
    ds = dicom.read_file("/var/www/Radionomics/Dicoms/normal/i382179.dcm")
    im = PILConverter.get_PIL_image(ds)
    print list(im.getdata())
