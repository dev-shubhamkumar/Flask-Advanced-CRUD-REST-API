from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

## Custom field in Marshmallow
class FileStorgaeField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs) -> FileStorage:
        if value is None:
            return None
        
        if not isinstance(value, FileStorage):
            self.fail("invalid")    # raises Validation Error
        
        return value


class ImageSchema(Schema):
    image = FileStorgaeField(required=True) 