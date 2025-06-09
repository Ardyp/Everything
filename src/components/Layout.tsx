import { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import {
  ChartBarIcon,
  FolderIcon,
  CpuChipIcon,
  HomeIcon,
} from '@heroicons/react/24/outline';
import VoiceControl from './VoiceControl';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'System Info', href: '/system', icon: ChartBarIcon },
  { name: 'File System', href: '/files', icon: FolderIcon },
  { name: 'Processes', href: '/processes', icon: CpuChipIcon },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleVoiceCommand = (command: string) => {
    // Simple command handling - can be expanded based on needs
    const commandLower = command.toLowerCase();
    
    if (commandLower.includes('dashboard') || commandLower.includes('home')) {
      navigate('/');
    } else if (commandLower.includes('system info') || commandLower.includes('system information')) {
      navigate('/system');
    } else if (commandLower.includes('file') || commandLower.includes('files')) {
      navigate('/files');
    } else if (commandLower.includes('process') || commandLower.includes('processes')) {
      navigate('/processes');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col">
        <div className="flex min-h-0 flex-1 flex-col border-r border-gray-200 bg-white">
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            <div className="flex flex-shrink-0 items-center px-4">
              <h1 className="text-2xl font-bold text-gray-900">OS Manager</h1>
            </div>
            <nav className="mt-5 flex-1 space-y-1 bg-white px-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="group flex items-center px-2 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  <item.icon
                    className="mr-3 h-6 w-6 flex-shrink-0 text-gray-400 group-hover:text-gray-500"
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col md:pl-64">
        <main className="flex-1">
          <div className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>

      {/* Voice Control */}
      <VoiceControl onCommand={handleVoiceCommand} />
    </div>
  );
} 