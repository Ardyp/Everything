interface SystemInfo {
  cpu_percent: number;
  memory: {
    used_gb: number;
    total_gb: number;
    percent: number;
  };
  disk: {
    used_gb: number;
    total_gb: number;
    percent: number;
  };
}

// Base URL for API requests. Falls back to localhost when the
// EXPO_PUBLIC_API_URL environment variable isn't defined.
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchSystemInfo(): Promise<SystemInfo> {
  const response = await fetch(`${API_BASE_URL}/system/info`);
  if (!response.ok) {
    throw new Error('Failed to fetch system info');
  }
  return response.json();
}

export async function fetchProcesses(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/processes`);
  if (!response.ok) {
    throw new Error('Failed to fetch processes');
  }
  return response.json();
}

export async function fetchFiles(path: string = '/'): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/files?path=${encodeURIComponent(path)}`);
  if (!response.ok) {
    throw new Error('Failed to fetch files');
  }
  return response.json();
} 