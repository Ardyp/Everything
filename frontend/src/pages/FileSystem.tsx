import { useEffect, useState } from 'react';
import axios from 'axios';

interface FileInfo {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  created: string;
  modified: string;
  permissions: string;
}

export default function FileSystem() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHidden, setShowHidden] = useState(false);

  const fetchFiles = async (path: string) => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/files/list?path=${encodeURIComponent(path)}&show_hidden=${showHidden}`);
      setFiles(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch directory contents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles(currentPath);
  }, [currentPath, showHidden]);

  const formatSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  const navigateToParent = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
  };

  const navigateToPath = (path: string) => {
    setCurrentPath(path);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">File System</h1>
          <p className="mt-2 text-sm text-gray-700">
            Current path: {currentPath}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              checked={showHidden}
              onChange={(e) => setShowHidden(e.target.checked)}
            />
            <span className="ml-2 text-sm text-gray-900">Show hidden files</span>
          </label>
        </div>
      </div>

      <div className="mt-6">
        <div className="-mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Name
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Size
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Modified
                    </th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Permissions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {currentPath !== '/' && (
                    <tr>
                      <td
                        className="whitespace-nowrap px-3 py-4 text-sm text-indigo-600 cursor-pointer hover:text-indigo-900"
                        onClick={navigateToParent}
                      >
                        ..
                      </td>
                      <td colSpan={3}></td>
                    </tr>
                  )}
                  {files.map((file) => (
                    <tr key={file.path}>
                      <td
                        className={`whitespace-nowrap px-3 py-4 text-sm ${
                          file.type === 'directory'
                            ? 'text-indigo-600 cursor-pointer hover:text-indigo-900'
                            : 'text-gray-900'
                        }`}
                        onClick={() => file.type === 'directory' && navigateToPath(file.path)}
                      >
                        {file.name}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {formatSize(file.size)}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {formatDate(file.modified)}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {file.permissions}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 