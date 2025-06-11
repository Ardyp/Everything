import { useState } from 'react';
import { View, Pressable } from 'react-native';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';

export default function VoiceCommandButton() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = async () => {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) return;
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
      setIsRecording(true);
    } catch (err) {
      console.warn('Could not start recording', err);
    }
  };

  const stopRecording = async () => {
    try {
      if (!recording) return;
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setIsRecording(false);
      const form = new FormData();
      form.append('audio', { uri, name: 'command.wav', type: 'audio/wav' } as any);
      const res = await fetch('http://localhost:8000/voice/command', { method: 'POST', body: form });
      const blob = await res.blob();
      const { sound } = await Audio.Sound.createAsync({ uri: URL.createObjectURL(blob) });
      await sound.playAsync();
    } catch (err) {
      console.warn('Recording error', err);
    } finally {
      setRecording(null);
    }
  };

  const toggle = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  return (
    <View style={{ position: 'absolute', bottom: 20, right: 20 }}>
      <Pressable onPress={toggle} style={{ backgroundColor: '#6366f1', padding: 16, borderRadius: 50 }}>
        <Ionicons name={isRecording ? 'stop' : 'mic'} size={24} color="white" />
      </Pressable>
    </View>
  );
}
