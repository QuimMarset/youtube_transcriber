import os
from pytube import YouTube
from pytube import exceptions



class YVDException(Exception):
    pass



class YoutubeVideoDownloader:


    def __init__(self, logger, save_path):
        self.logger = logger
        self.save_path = save_path
    

    def download_video_audio(self, url):
        try:    
            yt = YouTube(url)
            video_stream = yt.streams.filter(only_audio=True).first()
            audio_path = video_stream.download(self.save_path, f'video_{yt.video_id}.mp4')            
            self.logger.info(f'The video {url} audio was stored in {audio_path}')
            return audio_path
        
        except exceptions.AgeRestrictedError:
            raise YVDException(f'The video {url} has age restriction and cannot be downloaded')
        except exceptions.MembersOnly:
            raise YVDException(f'The video {url} has membership restriction and cannot be downloaded')
        except exceptions.LiveStreamError:
            raise YVDException(f'The video {url} is currently being live-streamed and cannot be downloaded')
        except exceptions.VideoPrivate:
            raise YVDException(f'The video {url} is private and cannot be downloaded')
        except exceptions.VideoUnavailable:
            raise YVDException(f'The video {url} is not available anymore')
        except exceptions.RegexMatchError:
            raise YVDException(f'{url} is not a valid Youtube video URL')
        except exceptions.PytubeError as exception:
            raise YVDException(str(exception))
        

    def delete_stored_video_audio(self, audio_path):
        if os.path.exists(audio_path):
            os.remove(audio_path)
            self.logger.info(f'Deleted downloaded video {audio_path}')
        else:
            self.logger.warning(f'The video in {audio_path} was already deleted')