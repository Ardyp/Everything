import { useQuery } from '@tanstack/react-query';
import { ScrollView, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { fetchSystemInfo } from '@/api/system';

export default function SystemInfoScreen() {
  const { data: systemInfo, isLoading, error } = useQuery({
    queryKey: ['systemInfo'],
    queryFn: fetchSystemInfo,
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  if (isLoading) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Loading system information...</ThemedText>
      </ThemedView>
    );
  }

  if (error) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Error loading system information</ThemedText>
        <ThemedText type="defaultSemiBold">{(error as Error).message}</ThemedText>
      </ThemedView>
    );
  }

  if (!systemInfo) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>No system information available</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ScrollView style={styles.scrollView}>
      <ThemedView style={styles.container}>
        <ThemedView style={styles.card}>
          <ThemedText type="subtitle">CPU Usage</ThemedText>
          <ThemedText>{systemInfo.cpu_percent}%</ThemedText>
        </ThemedView>

        <ThemedView style={styles.card}>
          <ThemedText type="subtitle">Memory</ThemedText>
          <ThemedText>Used: {systemInfo.memory.used_gb.toFixed(1)} GB</ThemedText>
          <ThemedText>Total: {systemInfo.memory.total_gb.toFixed(1)} GB</ThemedText>
          <ThemedText>Usage: {systemInfo.memory.percent}%</ThemedText>
        </ThemedView>

        <ThemedView style={styles.card}>
          <ThemedText type="subtitle">Disk</ThemedText>
          <ThemedText>Used: {systemInfo.disk.used_gb.toFixed(1)} GB</ThemedText>
          <ThemedText>Total: {systemInfo.disk.total_gb.toFixed(1)} GB</ThemedText>
          <ThemedText>Usage: {systemInfo.disk.percent}%</ThemedText>
        </ThemedView>
      </ThemedView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  container: {
    flex: 1,
    padding: 16,
    gap: 16,
  },
  card: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    gap: 8,
  },
});
