import { Ionicons } from '@expo/vector-icons';

interface IconSymbolProps {
  name: keyof typeof Ionicons.glyphMap;
  color: string;
  size: number;
}

export function IconSymbol({ name, color, size }: IconSymbolProps) {
  return <Ionicons name={name} size={size} color={color} />;
} 