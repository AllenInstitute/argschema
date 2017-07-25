from pathlib import Path
import marshmallow as mm
import collections, imghdr, logging

class ImageBatch(mm.fields.Field):
    """Specify a batch of images.  The input value should be a directory name
    containing supported images. The images should be sortable by filename.
    """

    def _validate(self, imagelist):
        # imghdr.what() should never throw here, because that was checked in _deserialize()
        format_map = collections.Counter([imghdr.what(str(p)) for p in imagelist])
        if not format_map:
            raise mm.ValidationError('no supported images found')
        for imagetype, count in format_map.items():
            logging.info('batching {} {} images'.format(count, imagetype))

    def _deserialize(self, value, attr, obj):
        logging.debug('queuing image batch from {}'.format(value))
        path = Path(str(value))
        if not path.is_dir():
            raise mm.ValidationError('{} is not a valid directory'.format(path))

        batch = []
        for file in path.iterdir():
            try:
                if imghdr.what(str(file)):
                    batch.append(file)
            except IOError:
                logging.warn('{} exists, but not readable'.format(file))
        return sorted(batch)
 
