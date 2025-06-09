import { BlurView } from 'expo-blur';
import { Platform, StyleSheet } from 'react-native';

export default function TabBarBackground() {
  if (Platform.OS === 'ios') {
    return <BlurView intensity={50} style={StyleSheet.absoluteFill} />;
  }
  return null;
} 