
class Video:
  def __init__(self, stream_fps):
    self.stream_fps = stream_fps

  def __repr__(self):
    summary = "(Video FPS: {})".format(self.stream_fps)
    return summary

  def to_map(self):
    return {
            "stream_fps": self.stream_fps
            }
    
