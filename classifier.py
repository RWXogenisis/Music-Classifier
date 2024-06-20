from collections import Counter
import numpy as np
import tensorflow as tf
import tensorflow_io as tfio
import matplotlib.pyplot as plt
import librosa

class Model:
    def __init__(self, model_path):
        self.loaded_model = tf.keras.models.load_model(model_path)

    def predict_genre(self, audio_slices):
        yhat = self.loaded_model.predict(audio_slices)
        predicted_classes = np.argmax(yhat, axis=1)
        return predicted_classes

class AudioProcessor:
    @staticmethod
    def load_wav_16k_mono(filename):
        res = tfio.audio.AudioIOTensor(filename)
        tensor = res.to_tensor()
        tensor = tf.math.reduce_sum(tensor, axis=1) / 2
        sample_rate = res.rate
        sample_rate = tf.cast(sample_rate, dtype=tf.int64)
        wav = tfio.audio.resample(tensor, rate_in=sample_rate, rate_out=16000)
        return wav

    @staticmethod
    def preprocess_wav(sample, index=None):  # Make index an optional argument
        sample = sample[0]
        zero_padding = tf.zeros([80000] - tf.shape(sample), dtype=tf.float32)
        wav = tf.concat([zero_padding, sample], 0)
        spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
        spectrogram = tf.abs(spectrogram)
        spectrogram = tf.expand_dims(spectrogram, axis=2)
        return spectrogram

class Controller:
    def __init__(self, model_path, audio_path):
        self.model = Model(model_path)
        self.audio_processor = AudioProcessor()
        self.audio_path = audio_path
        self.audio_slices = None

    def load_audio(self):
        wav = self.audio_processor.load_wav_16k_mono(self.audio_path)
        self.audio_slices = tf.keras.utils.timeseries_dataset_from_array(
            wav, wav, sequence_length=80000, sequence_stride=40000, batch_size=1
        )

    def process_audio(self):
        self.audio_slices = self.audio_slices.map(self.audio_processor.preprocess_wav)
        self.audio_slices = self.audio_slices.batch(64)

    def determine_genre(self):
        predicted_classes = self.model.predict_genre(self.audio_slices)
        element_counts = Counter(predicted_classes)
        sorted_elements = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_elements

    def save_mel_spectrogram(self):
        # Load the audio file
        audio, sample_rate = librosa.load(self.audio_path, sr=None)

        # Resample to 16kHz if needed
        target_sample_rate = 16000
        if sample_rate != target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=target_sample_rate)

        # Create the mel spectrogram
        mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=target_sample_rate)
        mel_db = librosa.power_to_db(mel_spectrogram, ref=np.max)

        # Plot and save the mel spectrogram
        plt.figure(figsize=(8, 6))
        librosa.display.specshow(mel_db, x_axis='time', y_axis='mel', sr=target_sample_rate, cmap='viridis')
        plt.colorbar(format='%+2.0f dB')
        plt.savefig("pic.png", bbox_inches='tight', pad_inches=0)
        plt.close()


if __name__ == "__main__":
    model_path = 'C:\\Users\\S Karun Vikhash\\Downloads\\ADS\\OOAD\\GITZLAB\\model.h5'
    audio_path = 'C:\\Users\\S Karun Vikhash\\Downloads\\ADS\\OOAD\\temp.wav'

    controller = Controller(model_path, audio_path)
    controller.load_audio()
    controller.process_audio()
    sorted_elements = controller.determine_genre()

    print("Determining the genre of the song...")
    genre_dict = {0: "classical",1: "hiphop",2: "jazz",3: "pop",4: "rock"}
    for element, count in sorted_elements:
        print(f"{genre_dict[element]}, Frequency: {count}")
    # Save the mel spectrogram as an image
    controller.save_mel_spectrogram()


#0 is for classical
#1 is for hiphop
#2 is for jazz
#3 is for pop
#4 is for rock
