import odrive
import fibre


def obj_to_path(root, obj):
    for key in dir(root):
        value = getattr(root, key)
        if not key.startswith('_') and \
                isinstance(value, fibre.libfibre.RemoteObject):
            if value == obj:
                return key
            sub_path = self.obj_to_path(value, obj)
            if sub_path is not None:
                return key + "." + sub_path
    return None


def decode_to_dict(root, obj, is_config_object):
    result = {}
    for key in dir(obj):
        value = getattr(obj, key)
        if key.startswith('_') and key.endswith(
                '_property') and is_config_object:
            value = value.read()
            if isinstance(value, fibre.libfibre.RemoteObject):
                value = obj_to_path(root, value)
            result[key[1:-9]] = value
        elif not key.startswith('_') and \
                isinstance(value, fibre.libfibre.RemoteObject):
            sub_dict = decode_to_dict(root, value,
                                      (key == 'config') or is_config_object)
            if sub_dict != {}:
                result[key] = sub_dict
    return result
