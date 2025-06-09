import { useQuery } from '@tanstack/react-query';
import { FlatList, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

interface FileInfo {
  name: string;
  path: string;
  size: number;
  type: 'file' | 'directory';
  modified: string;
}

async function fetchFiles(path: string = '/'): Promise<FileInfo[]> {
  const response = await fetch(`http://localhost:8000/files?path=${encodeURIComponent(path)}`);
  if (!response.ok) {
    throw new Error('Failed to fetch files');
  }
  return response.json();
}

function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

export default function FilesScreen() {
  const { data: files, isLoading, error } = useQuery({
    queryKey: ['files', '/'],
    queryFn: () => fetchFiles('/'),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Loading files...</ThemedText>
      </ThemedView>
    );
  }

  if (error) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Error loading files</ThemedText>
        <ThemedText type="defaultSemiBold">{(error as Error).message}</ThemedText>
      </ThemedView>
    );
  }

  return (
    <FlatList
      style={styles.container}
      data={files}
      keyExtractor={(item) => item.path}
      renderItem={({ item }) => (
        <ThemedView style={styles.fileItem}>
          <ThemedText type="subtitle">{item.name}</ThemedText>
          <ThemedText>Type: {item.type}</ThemedText>
          {item.type === 'file' && (
            <ThemedText>Size: {formatFileSize(item.size)}</ThemedText>
          )}
          <ThemedText>Modified: {new Date(item.modified).toLocaleString()}</ThemedText>
        </ThemedView>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  fileItem: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    marginBottom: 8,
    gap: 4,
  },
}); 