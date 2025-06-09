import { useQuery } from '@tanstack/react-query';
import { FlatList, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

interface Process {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status: string;
}

async function fetchProcesses(): Promise<Process[]> {
  const response = await fetch('http://localhost:8000/processes');
  if (!response.ok) {
    throw new Error('Failed to fetch processes');
  }
  return response.json();
}

export default function ProcessesScreen() {
  const { data: processes, isLoading, error } = useQuery({
    queryKey: ['processes'],
    queryFn: fetchProcesses,
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Loading processes...</ThemedText>
      </ThemedView>
    );
  }

  if (error) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Error loading processes</ThemedText>
        <ThemedText type="defaultSemiBold">{(error as Error).message}</ThemedText>
      </ThemedView>
    );
  }

  return (
    <FlatList
      style={styles.container}
      data={processes}
      keyExtractor={(item) => item.pid.toString()}
      renderItem={({ item }) => (
        <ThemedView style={styles.processItem}>
          <ThemedText type="subtitle">{item.name}</ThemedText>
          <ThemedText>PID: {item.pid}</ThemedText>
          <ThemedText>CPU: {item.cpu_percent.toFixed(1)}%</ThemedText>
          <ThemedText>Memory: {item.memory_percent.toFixed(1)}%</ThemedText>
          <ThemedText>Status: {item.status}</ThemedText>
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
  processItem: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    marginBottom: 8,
    gap: 4,
  },
}); 