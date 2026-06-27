/*
  Faun SDL2 Audio Queue backend for Emscripten / Web
  
  This driver maps Faun mixed PCM audio writes to SDL2's Queue Audio API,
  which Emscripten translates directly to low-latency Web Audio API calls.
*/

#include <SDL2/SDL.h>

typedef struct {
    SDL_AudioDeviceID dev;
} SdlAudioSession;

static SdlAudioSession sdlSession;

static void sysaudio_close(void)
{
    SDL_QuitSubSystem(SDL_INIT_AUDIO);
}

static const char* sysaudio_open(const char* appName)
{
    (void) appName;
    if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {
        return "SDL_InitSubSystem(SDL_INIT_AUDIO) failed";
    }
    return NULL;
}

static const char* sysaudio_allocVoice(FaunVoice* voice, int updateHz,
                                       const char* appName)
{
    SdlAudioSession* s = &sdlSession;
    SDL_AudioSpec desired, obtained;
    int chan;

    (void) updateHz;
    (void) appName;

    chan = faun_channelCount(voice->mix.chanLayout);

    memset(&desired, 0, sizeof(desired));
    desired.freq     = voice->mix.rate;
    desired.channels = chan;
    desired.samples  = voice->mix.avail;

    switch (voice->mix.format) {
        case FAUN_U8:
            desired.format = AUDIO_U8;
            break;
        case FAUN_S16:
            desired.format = AUDIO_S16SYS;
            break;
        case FAUN_F32:
        default:
            desired.format = AUDIO_F32SYS;
            break;
    }

    // Open audio device in queue mode (no callback, queue-based play)
    s->dev = SDL_OpenAudioDevice(NULL, 0, &desired, &obtained, 0);
    if (s->dev == 0) {
        return SDL_GetError();
    }

    voice->backend = s;
    return NULL;
}

static void sysaudio_freeVoice(FaunVoice* voice)
{
    SdlAudioSession* s = (SdlAudioSession*) voice->backend;
    if (s && s->dev) {
        SDL_CloseAudioDevice(s->dev);
        s->dev = 0;
        voice->backend = NULL;
    }
}

static const char* sysaudio_write(FaunVoice* voice, const void* data,
                                  uint32_t len)
{
    SdlAudioSession* s = (SdlAudioSession*) voice->backend;
    if (s && s->dev) {
        if (SDL_QueueAudio(s->dev, data, len) < 0) {
            return SDL_GetError();
        }
    }
    return NULL;
}

static int sysaudio_startVoice(FaunVoice* voice)
{
    SdlAudioSession* s = (SdlAudioSession*) voice->backend;
    if (s && s->dev) {
        SDL_PauseAudioDevice(s->dev, 0);
    }
    return 1;
}

static int sysaudio_stopVoice(FaunVoice* voice)
{
    SdlAudioSession* s = (SdlAudioSession*) voice->backend;
    if (s && s->dev) {
        SDL_PauseAudioDevice(s->dev, 1);
    }
    return 1;
}
