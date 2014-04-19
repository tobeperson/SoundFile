import numpy as np
from cffi import FFI
from os import SEEK_SET, SEEK_CUR, SEEK_END

"""PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through libsndfile[1], which is a free, cross-platform,
open-source library for reading and writing many different sampled
sound file formats that runs on many platforms including Windows, OS
X, and Unix. It is accessed through CFFI[2], which is a foreight
function interface for Python calling C code. CFFI is supported for
CPython 2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as
NumPy arrays.

[1]: http://www.mega-nerd.com/libsndfile/
[2]: http://cffi.readthedocs.org/

Every sound file is represented as a SoundFile object. SoundFiles can
be created for reading, writing, or both. Each SoundFile has a
sample_rate, a number of channels, and a file format. These can not be
changed at runtime.

A SoundFile has methods for reading and writing data to/from the file.
Even though every sound file has a fixed file format, reading and
writing is possible in four different NumPy formats: int16, int32,
float32 and float64.

At the same time, SoundFiles act as sequence types, so you can use
slices to read or write data as well. Since there is no way of
specifying data formats for slices, the SoundFile will always return
float64 data for those.

Note that you need to have libsndfile installed in order to use
PySoundFile. On Windows, you need to rename the library to
"sndfile.dll".

PySoundFile is BSD licensed.
(c) 2013, Bastian Bechtold

"""

ffi = FFI()
ffi.cdef("""
typedef int64_t sf_count_t ;

typedef struct SNDFILE_tag SNDFILE ;

typedef struct SF_INFO
{
    sf_count_t frames ;        /* Used to be called samples.  Changed to avoid confusion. */
    int        samplerate ;
    int        channels ;
    int        format ;
    int        sections ;
    int        seekable ;
} SF_INFO ;

SNDFILE*    sf_open          (const char *path, int mode, SF_INFO *sfinfo) ;
int         sf_format_check  (const SF_INFO *info) ;

sf_count_t  sf_seek          (SNDFILE *sndfile, sf_count_t frames, int whence) ;

int         sf_command       (SNDFILE *sndfile, int cmd, void *data, int datasize) ;

int         sf_error         (SNDFILE *sndfile) ;
const char* sf_strerror      (SNDFILE *sndfile) ;
const char* sf_error_number  (int errnum) ;

int         sf_perror        (SNDFILE *sndfile) ;
int         sf_error_str     (SNDFILE *sndfile, char* str, size_t len) ;

int         sf_close         (SNDFILE *sndfile) ;
void        sf_write_sync    (SNDFILE *sndfile) ;

sf_count_t  sf_read_short    (SNDFILE *sndfile, short *ptr, sf_count_t items) ;
sf_count_t  sf_read_int      (SNDFILE *sndfile, int *ptr, sf_count_t items) ;
sf_count_t  sf_read_float    (SNDFILE *sndfile, float *ptr, sf_count_t items) ;
sf_count_t  sf_read_double   (SNDFILE *sndfile, double *ptr, sf_count_t items) ;

sf_count_t  sf_readf_short   (SNDFILE *sndfile, short *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_int     (SNDFILE *sndfile, int *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_float   (SNDFILE *sndfile, float *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_double  (SNDFILE *sndfile, double *ptr, sf_count_t frames) ;

sf_count_t  sf_write_short   (SNDFILE *sndfile, short *ptr, sf_count_t items) ;
sf_count_t  sf_write_int     (SNDFILE *sndfile, int *ptr, sf_count_t items) ;
sf_count_t  sf_write_float   (SNDFILE *sndfile, float *ptr, sf_count_t items) ;
sf_count_t  sf_write_double  (SNDFILE *sndfile, double *ptr, sf_count_t items) ;

sf_count_t  sf_writef_short  (SNDFILE *sndfile, short *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_int    (SNDFILE *sndfile, int *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_float  (SNDFILE *sndfile, float *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_double (SNDFILE *sndfile, double *ptr, sf_count_t frames) ;

sf_count_t  sf_read_raw      (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;
sf_count_t  sf_write_raw     (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;

const char* sf_get_string    (SNDFILE *sndfile, int str_type) ;
int         sf_set_string    (SNDFILE *sndfile, int str_type, const char* str) ;

typedef sf_count_t  (*sf_vio_get_filelen) (void *user_data) ;
typedef sf_count_t  (*sf_vio_seek)        (sf_count_t offset, int whence, void *user_data) ;
typedef sf_count_t  (*sf_vio_read)        (void *ptr, sf_count_t count, void *user_data) ;
typedef sf_count_t  (*sf_vio_write)       (const void *ptr, sf_count_t count, void *user_data) ;
typedef sf_count_t  (*sf_vio_tell)        (void *user_data) ;

typedef struct SF_VIRTUAL_IO
{    sf_count_t  (*get_filelen) (void *user_data) ;
     sf_count_t  (*seek)        (sf_count_t offset, int whence, void *user_data) ;
     sf_count_t  (*read)        (void *ptr, sf_count_t count, void *user_data) ;
     sf_count_t  (*write)       (const void *ptr, sf_count_t count, void *user_data) ;
     sf_count_t  (*tell)        (void *user_data) ;
} SF_VIRTUAL_IO ;

SNDFILE*    sf_open_virtual   (SF_VIRTUAL_IO *sfvirtual, int mode, SF_INFO *sfinfo, void *user_data) ;

""")

_open_modes = {
    0x10: 'READ',
    0x20: 'WRITE',
    0x30: 'RDWR'
}

_str_types = {
    'title':       0x01,
    'copyright':   0x02,
    'software':    0x03,
    'artist':      0x04,
    'comment':     0x05,
    'date':        0x06,
    'album':       0x07,
    'license':     0x08,
    'tracknumber': 0x09,
    'genre':       0x10,
}

snd_types = {
    'WAV':   0x010000, # Microsoft WAV format (little endian default).
    'AIFF':  0x020000, # Apple/SGI AIFF format (big endian).
    'AU':    0x030000, # Sun/NeXT AU format (big endian).
    'RAW':   0x040000, # RAW PCM data.
    'PAF':   0x050000, # Ensoniq PARIS file format.
    'SVX':   0x060000, # Amiga IFF / SVX8 / SV16 format.
    'NIST':  0x070000, # Sphere NIST format.
    'VOC':   0x080000, # VOC files.
    'IRCAM': 0x0A0000, # Berkeley/IRCAM/CARL
    'W64':   0x0B0000, # Sonic Foundry's 64 bit RIFF/WAV
    'MAT4':  0x0C0000, # Matlab (tm) V4.2 / GNU Octave 2.0
    'MAT5':  0x0D0000, # Matlab (tm) V5.0 / GNU Octave 2.1
    'PVF':   0x0E0000, # Portable Voice Format
    'XI':    0x0F0000, # Fasttracker 2 Extended Instrument
    'HTK':   0x100000, # HMM Tool Kit format
    'SDS':   0x110000, # Midi Sample Dump Standard
    'AVR':   0x120000, # Audio Visual Research
    'WAVEX': 0x130000, # MS WAVE with WAVEFORMATEX
    'SD2':   0x160000, # Sound Designer 2
    'FLAC':  0x170000, # FLAC lossless file format
    'CAF':   0x180000, # Core Audio File format
    'WVE':   0x190000, # Psion WVE format
    'OGG':   0x200000, # Xiph OGG container
    'MPC2K': 0x210000, # Akai MPC 2000 sampler
    'RF64':  0x220000  # RF64 WAV file
}

snd_subtypes = {
    'PCM_S8':    0x0001, # Signed 8 bit data
    'PCM_16':    0x0002, # Signed 16 bit data
    'PCM_24':    0x0003, # Signed 24 bit data
    'PCM_32':    0x0004, # Signed 32 bit data
    'PCM_U8':    0x0005, # Unsigned 8 bit data (WAV and RAW only)
    'FLOAT':     0x0006, # 32 bit float data
    'DOUBLE':    0x0007, # 64 bit float data
    'ULAW':      0x0010, # U-Law encoded.
    'ALAW':      0x0011, # A-Law encoded.
    'IMA_ADPCM': 0x0012, # IMA ADPCM.
    'MS_ADPCM':  0x0013, # Microsoft ADPCM.
    'GSM610':    0x0020, # GSM 6.10 encoding.
    'VOX_ADPCM': 0x0021, # OKI / Dialogix ADPCM
    'G721_32':   0x0030, # 32kbs G721 ADPCM encoding.
    'G723_24':   0x0031, # 24kbs G723 ADPCM encoding.
    'G723_40':   0x0032, # 40kbs G723 ADPCM encoding.
    'DWVW_12':   0x0040, # 12 bit Delta Width Variable Word encoding.
    'DWVW_16':   0x0041, # 16 bit Delta Width Variable Word encoding.
    'DWVW_24':   0x0042, # 24 bit Delta Width Variable Word encoding.
    'DWVW_N':    0x0043, # N bit Delta Width Variable Word encoding.
    'DPCM_8':    0x0050, # 8 bit differential PCM (XI only)
    'DPCM_16':   0x0051, # 16 bit differential PCM (XI only)
    'VORBIS':    0x0060, # Xiph Vorbis encoding.
}

snd_endians = {
    'FILE':   0x00000000, # Default file endian-ness.
    'LITTLE': 0x10000000, # Force little endian-ness.
    'BIG':    0x20000000, # Force big endian-ness.
    'CPU':    0x30000000, # Force CPU endian-ness.
}

wave_file = ('WAV', 'PCM_16', 'FILE')
flac_file = ('FLAC', 'PCM_16', 'FILE')
matlab_file = ('MAT5', 'DOUBLE', 'FILE')
ogg_file = ('OGG', 'VORBIS', 'FILE')

def _encodeformat(format):
    type = snd_types[format[0]]
    subtype = snd_subtypes[format[1]]
    endianness = snd_endians[format[2]]
    return type|subtype|endianness

def _decodeformat(format):
    sub_mask  = 0x0000FFFF
    type_mask = 0x0FFF0000
    end_mask  = 0x30000000

    def reverse_dict(d): return {value:key for key, value in d.items()}

    type = reverse_dict(snd_types)[format & type_mask]
    subtype = reverse_dict(snd_subtypes)[format & sub_mask]
    endianness = reverse_dict(snd_endians)[format & end_mask]

    return (type, subtype, endianness)


class _ModeType(int):
    def __repr__(self):
        return _open_modes.get(self, int.__repr__(self))


def _add_constants_to_module_namespace(constants_dict, constants_type):
    for k, v in constants_dict.items():
        globals()[v] = constants_type(k)

_add_constants_to_module_namespace(_open_modes, _ModeType)

_snd = ffi.dlopen('sndfile')


class SoundFile(object):

    """SoundFile handles reading and writing to sound files.

    Each SoundFile opens one sound file on the disk. This sound file
    has a specific samplerate, data format and a set number of
    channels. Each sound file can be opened with one of the modes
    READ/WRITE/RDWR. Note that RDWR is unsupported for some formats.

    Data can be written to the file using write(), or read from the
    file using read(). Every read and write operation starts at a
    certain position in the file. Reading N frames will change this
    position by N frames as well. Alternatively, seek()
    can be used to set the current position to a frame
    index offset from the current position, the start of the file, or
    the end of the file, respectively.

    Alternatively, slices can be used to access data at arbitrary
    positions in the file. Note that slices currently only work on
    frame indices, not channels. The quickest way to read in a whole
    file as a float64 NumPy array is in fact SoundFile('filename')[:].

    All data access uses frames as index. A frame is one discrete
    time-step in the sound file. Every frame contains as many samples
    as there are channels in the file.

    In addition to audio data, there are a number of text fields in
    every sound file. In particular, you can set a title, a copyright
    notice, a software description, the artist name, a comment, a
    date, the album name, a license, a tracknumber and a genre. Note
    however, that not all of these fields are supported for every file
    format.

    """

    def __init__(self, name, mode=READ, sample_rate=0, channels=0, format=0,
                 virtual_io=False):
        """Open a new SoundFile.

        If a file is opened with mode READ or WRITE,
        no sample_rate, channels or file format need to be given. If a
        file is opened with mode RDWR, you must provide a sample_rate,
        a number of channels, and a file format. An exception is the
        RAW data format, which requires these data points for reading
        as well.

        Instead of the library constants READ/WRITE/RDWR you can also
        use the (case-insensitive) strings 'r'/'w'/'rw' or
        'READ'/'WRITE'/'RDWR'.

        File formats consist of three parts:
        - one of the file types from snd_types
        - one of the data types from snd_subtypes
        - an endianness from snd_endians
        and can be either a tuple of three strings indicate the keys,
        or an OR'ed together integer of them.

        Since this is somewhat burdensome if you have to do it for
        every new file, you can use one of the commonly used
        pre-defined types wave_file, flac_file, matlab_file or
        ogg_file.

        """
        info = ffi.new("SF_INFO*")
        info.samplerate = sample_rate
        info.channels = channels
        if hasattr(format, '__getitem__'):
            format = _encodeformat(format)
        info.format = format

        if isinstance(mode, str):
            try:
                mode = {'read':  READ,  'r':  READ,
                        'write': WRITE, 'w':  WRITE,
                        'rdwr':  RDWR,  'rw': RDWR}[mode.lower()]
            except KeyError:
                pass
        if not isinstance(mode, _ModeType):
            raise ValueError("Invalid mode: %s" % repr(mode))
        self.mode = mode

        if virtual_io:
            fObj = name
            for attr in ('seek', 'read', 'write', 'tell'):
                if not hasattr(fObj, attr):
                    msg = 'File-like object must have: "%s"' % attr
                    raise RuntimeError(msg)
            self._vio = self._init_vio(fObj)
            vio = ffi.new("SF_VIRTUAL_IO*", self._vio)
            self._vio['vio_cdata'] = vio
            self._file = _snd.sf_open_virtual(vio, mode, info, ffi.NULL)
        else:
            filename = ffi.new('char[]', name.encode())
            self._file = _snd.sf_open(filename, mode, info)

        self._handle_error()

        self.frames = info.frames
        self.sample_rate = info.samplerate
        self.channels = info.channels
        self.format = _decodeformat(info.format)
        self.sections = info.sections
        self.seekable = info.seekable == 1

    closed = property(lambda self: self._file is None)

    # avoid confusion if something goes wrong before assigning self._file:
    _file = None

    def _init_vio(self, fObj):
        # Define callbacks here, so they can reference fObj / size
        @ffi.callback("sf_vio_get_filelen")
        def vio_get_filelen(user_data):
            # Streams must set _length or implement __len__
            if hasattr(fObj, '_length'):
                size = fObj._length
            elif not hasattr(fObj, '__len__'):
                old_file_position = fObj.tell()
                fObj.seek(0, SEEK_END)
                size = fObj.tell()
                fObj.seek(old_file_position, SEEK_SET)
            else:
                size = len(fObj)
            return size

        @ffi.callback("sf_vio_seek")
        def vio_seek(offset, whence, user_data):
            fObj.seek(offset, whence)
            curr = fObj.tell()
            return curr

        @ffi.callback("sf_vio_read")
        def vio_read(ptr, count, user_data):
            buf = ffi.buffer(ptr, count)
            data_read = fObj.readinto(buf)
            return data_read

        @ffi.callback("sf_vio_write")
        def vio_write(ptr, count, user_data):
            buf = ffi.buffer(ptr, count)
            data = buf[:]
            length = fObj.write(data)
            return length

        @ffi.callback("sf_vio_tell")
        def vio_tell(user_data):
            return fObj.tell()

        vio = {
            'get_filelen': vio_get_filelen,
            'seek': vio_seek,
            'read': vio_read,
            'write': vio_write,
            'tell': vio_tell,
        }
        return vio

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_error(self):
        # this checks the error flag of the SNDFILE* structure
        self._check_if_closed()
        err = _snd.sf_error(self._file)
        self._handle_error_number(err)

    def _handle_error_number(self, err):
        # pretty-print a numerical error code
        if err != 0:
            err_str = _snd.sf_error_number(err)
            raise RuntimeError(ffi.string(err_str).decode())

    def _check_if_closed(self):
        # check if the file is closed and raise an error if it is.
        # This should be used in every method that tries to access self._file.
        if self.closed:
            raise ValueError("I/O operation on closed file")

    def __setattr__(self, name, value):
        # access text data in the sound file through properties
        if name in _str_types:
            self._check_if_closed()
            if self.mode == READ:
                raise RuntimeError("Can not change %s of file in read mode" %
                                   name)
            data = ffi.new('char[]', value.encode())
            err = _snd.sf_set_string(self._file, _str_types[name], data)
            self._handle_error_number(err)
        else:
            super(SoundFile, self).__setattr__(name, value)

    def __getattr__(self, name):
        # access text data in the sound file through properties
        if name in _str_types:
            self._check_if_closed()
            data = _snd.sf_get_string(self._file, _str_types[name])
            if data == ffi.NULL:
                return ""
            else:
                return ffi.string(data).decode()
        else:
            raise AttributeError("SoundFile has no attribute %s" % name)

    def __len__(self):
        return self.frames

    def _get_slice_bounds(self, frame):
        # get start and stop index from slice, asserting step==1
        if not isinstance(frame, slice):
            frame = slice(frame, frame + 1)
        start, stop, step = frame.indices(len(self))
        if step != 1:
            raise RuntimeError("Step size must be 1!")
        if start > stop:
            stop = start
        return start, stop

    def __getitem__(self, frame):
        # access the file as if it where a Numpy array. The data is
        # returned as numpy array.
        second_frame = None
        if isinstance(frame, tuple):
            if len(frame) > 2:
                raise AttributeError(
                    "SoundFile can only be accessed in one or two dimensions")
            frame, second_frame = frame
        start, stop = self._get_slice_bounds(frame)
        curr = self.seek(0, SEEK_CUR | READ)
        self.seek(start, SEEK_SET | READ)
        data = self.read(stop - start)
        self.seek(curr, SEEK_SET | READ)
        if second_frame:
            return data[(slice(None), second_frame)]
        else:
            return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if self.mode == READ:
            raise RuntimeError("Cannot write to file opened in READ mode!")
        start, stop = self._get_slice_bounds(frame)
        if stop - start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), stop - start))
        curr = self.seek(0, SEEK_CUR | WRITE)
        self.seek(start, SEEK_SET | WRITE)
        self.write(data)
        self.seek(curr, SEEK_SET | WRITE)
        return data

    def flush(self):
        """Write unwritten data to disk."""
        self._check_if_closed()
        _snd.sf_write_sync(self._file)

    def close(self):
        """Close the file. Can be called multiple times."""
        if not self.closed:
            # be sure to flush data to disk before closing the file
            self.flush()
            err = _snd.sf_close(self._file)
            self._file = None
            self._handle_error_number(err)

    def seek(self, frames, whence=SEEK_SET):
        """Set the read and/or write position.

        By default (whence=SEEK_SET), frames are counted from the
        beginning of the file. SEEK_CUR seeks from the current position
        (positive and negative values are allowed).
        SEEK_END seeks from the end (use negative values).

        In RDWR mode, the whence argument can be combined (using
        logical or) with READ or WRITE in order to set only the read
        or write position, respectively (e.g. SEEK_SET | WRITE).

        To set the read/write position to the beginning of the file,
        use seek(0), to set it to right after the last frame,
        e.g. for appending new data, use seek(0, SEEK_END).

        Returns the new absolute read position in frames or a negative
        value on error.
        """
        self._check_if_closed()
        return _snd.sf_seek(self._file, frames, whence)

    def read(self, frames=-1, format=np.float64):
        """Read a number of frames from the file.

        Reads the given number of frames in the given data format from
        the current read position. This also advances the read
        position by the same number of frames.
        Use frames=-1 to read until the end of the file.

        Returns the read data as a (frames x channels) NumPy array.

        If there is not enough data left in the file to read, a
        smaller NumPy array will be returned.

        """
        self._check_if_closed()
        if self.mode == WRITE:
            raise RuntimeError("Cannot read from file opened in WRITE mode!")
        formats = {
            np.float64: 'double[]',
            np.float32: 'float[]',
            np.int32: 'int[]',
            np.int16: 'short[]'
        }
        readers = {
            np.float64: _snd.sf_readf_double,
            np.float32: _snd.sf_readf_float,
            np.int32: _snd.sf_readf_int,
            np.int16: _snd.sf_readf_short
        }
        if format not in formats:
            raise ValueError("Can only read int16, int32, float32 and float64")
        if frames < 0:
            curr = self.seek(0, SEEK_CUR | READ)
            frames = self.frames - curr
        data = ffi.new(formats[format], frames*self.channels)
        read = readers[format](self._file, data, frames)
        self._handle_error()
        np_data = np.frombuffer(ffi.buffer(data), dtype=format,
                                count=read*self.channels)
        return np.reshape(np_data, (read, self.channels))

    def write(self, data):
        """Write a number of frames to the file.

        Writes a number of frames to the current read position in the
        file. This also advances the read position by the same number
        of frames and enlarges the file if necessary.

        The data must be provided as a (frames x channels) NumPy
        array.

        """
        self._check_if_closed()
        if self.mode == READ:
            raise RuntimeError("Cannot write to file opened in READ mode!")
        formats = {
            np.dtype(np.float64): 'double*',
            np.dtype(np.float32): 'float*',
            np.dtype(np.int32): 'int*',
            np.dtype(np.int16): 'short*'
        }
        writers = {
            np.dtype(np.float64): _snd.sf_writef_double,
            np.dtype(np.float32): _snd.sf_writef_float,
            np.dtype(np.int32): _snd.sf_writef_int,
            np.dtype(np.int16): _snd.sf_writef_short
        }
        if data.dtype not in writers:
            raise ValueError("Data must be int16, int32, float32 or float64")
        raw_data = ffi.new('char[]', data.flatten().tostring())
        written = writers[data.dtype](self._file,
                                      ffi.cast(formats[data.dtype], raw_data),
                                      len(data))
        self._handle_error()
        return written
