import { StyleSheet, View } from 'react-native';
import { BlurView } from 'expo-blur';
import { Platform } from 'react-native';
import { Colors } from '@/constants/Colors';

export default function TabBarBackground() {
  if (Platform.OS === 'ios') {
    return <BlurView intensity={50} style={StyleSheet.absoluteFill} />;
  }
  return null;
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  androidBackground: {
    backgroundColor: Colors.card,
  },
}); 