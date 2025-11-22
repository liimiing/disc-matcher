import React, { useState, useRef, useEffect } from 'react';
import { Folder, FileUp, Download, Settings, ListMusic, RefreshCw, PlayCircle, Disc } from 'lucide-react';
import { AlbumEntry, ProcessingStatus, GlobalSettings, DiscogsSearchResult } from './types';
import { searchDiscogs } from './services/discogsService';
import { generateAlbumInsights } from './services/geminiService';
import AlbumCard from './components/AlbumCard';
import ConflictResolver from './components/ConflictResolver';

// --- Helpers ---
const generateCSV = (entries: AlbumEntry[]) => {
  const headers = ['FolderName', 'Files', 'Artist - Title', 'Year', 'Label', 'CatalogNo', 'Genre', 'Style', 'Country', 'AI_Vibe', 'CoverURL', 'DiscogsID'];
  const rows = entries.map(e => {
      const r = e.selectedRelease;
      return [
          `"${e.folderName.replace(/"/g, '""')}"`,
          e.files.length,
          `"${(r?.title || '').replace(/"/g, '""')}"`,
          r?.year || '',
          `"${(r?.label?.join(', ') || '').replace(/"/g, '""')}"`,
          r?.catno || '',
          `"${(r?.genre?.join(', ') || '').replace(/"/g, '""')}"`,
          `"${(r?.style?.join(', ') || '').replace(/"/g, '""')}"`,
          r?.country || '',
          `"${(e.aiAnalysis || '').replace(/"/g, '""')}"`,
          r?.cover_image || '',
          r?.id || ''
      ].join(',');
  });
  return [headers.join(','), ...rows].join('\n');
};

// --- Main Component ---
export default function App() {
  const [token, setToken] = useState<string>(''); // Store Discogs Token
  const [entries, setEntries] = useState<AlbumEntry[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingIndex, setProcessingIndex] = useState(0);
  
  // Modal State
  const [resolvingEntry, setResolvingEntry] = useState<AlbumEntry | null>(null);

  // File Input Ref
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load Token from local storage
  useEffect(() => {
    const stored = localStorage.getItem('discogs_token');
    if (stored) setToken(stored);
  }, []);

  const saveToken = (t: string) => {
    setToken(t);
    localStorage.setItem('discogs_token', t);
  };

  // Handle Folder Selection
  const handleFolderSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;

    const fileList = Array.from(event.target.files);
    // Group files by parent folder
    const folderMap = new Map<string, string[]>();

    fileList.forEach((file: any) => {
      const pathParts = file.webkitRelativePath.split('/');
      // Assuming Structure: Root / Artist / Album / Song.mp3 OR Root / Album / Song.mp3
      // We want to target the folder that contains the music.
      // Let's grab the *immediate parent* folder of the file.
      if (pathParts.length >= 2) {
        const folderPath = pathParts.slice(0, -1).join('/');
        const folderName = pathParts[pathParts.length - 2];
        
        // Only process folders with common audio extensions or relevant files
        if (/\.(mp3|flac|wav|m4a|aac|jpg|png)$/i.test(file.name)) {
             if (!folderMap.has(folderPath)) {
                folderMap.set(folderPath, []);
             }
             folderMap.get(folderPath)?.push(file.name);
        }
      }
    });

    const newEntries: AlbumEntry[] = Array.from(folderMap.entries()).map(([fullPath, files]) => {
        const parts = fullPath.split('/');
        return {
            id: fullPath,
            folderName: parts[parts.length - 1],
            fullPath,
            status: ProcessingStatus.PENDING,
            searchResults: [],
            selectedRelease: null,
            files
        };
    });

    setEntries(newEntries);
  };

  // Process Queue
  const startProcessing = async () => {
    if (!token) {
        alert("Please enter a Discogs Personal Access Token first.");
        return;
    }

    setIsProcessing(true);
    
    // Process one by one to avoid rate limits (naive implementation for demo)
    // In a real app, we might use p-limit or similar
    for (let i = 0; i < entries.length; i++) {
        if (entries[i].status !== ProcessingStatus.PENDING) continue;
        
        setProcessingIndex(i);

        // Update status to SEARCHING
        setEntries(prev => prev.map((e, idx) => idx === i ? { ...e, status: ProcessingStatus.SEARCHING } : e));

        // Search Discogs
        const results = await searchDiscogs(entries[i].folderName, token);
        
        // Analyze Results
        let status = ProcessingStatus.NEEDS_REVIEW;
        let selected: DiscogsSearchResult | null = null;

        if (results.length === 0) {
            status = ProcessingStatus.NOT_FOUND;
        } else if (results.length === 1) {
            status = ProcessingStatus.COMPLETED;
            selected = results[0];
        } else {
             // Check for exact string match to auto-select
             const exact = results.find(r => r.title.toLowerCase() === entries[i].folderName.toLowerCase());
             if (exact) {
                 status = ProcessingStatus.COMPLETED;
                 selected = exact;
             }
        }

        // If matched, optionally run AI analysis (Doing it here for demo effect)
        let aiText = "";
        if (selected) {
            aiText = await generateAlbumInsights(entries[i].folderName, selected);
        }

        // Update Entry
        setEntries(prev => prev.map((e, idx) => idx === i ? { 
            ...e, 
            status, 
            searchResults: results, 
            selectedRelease: selected,
            aiAnalysis: aiText
        } : e));

        // Rate Limit Delay (1s)
        await new Promise(resolve => setTimeout(resolve, 1100));
    }

    setIsProcessing(false);
  };

  // Handle Manual Selection
  const handleManualSelect = async (entry: AlbumEntry, release: DiscogsSearchResult) => {
     // Close modal
     setResolvingEntry(null);

     // Update state
     const aiText = await generateAlbumInsights(entry.folderName, release);
     
     setEntries(prev => prev.map(e => e.id === entry.id ? {
         ...e,
         status: ProcessingStatus.COMPLETED,
         selectedRelease: release,
         aiAnalysis: aiText
     } : e));
  };

  // Export
  const handleExport = () => {
      const csv = generateCSV(entries);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'album_metadata_export.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  // Calculated Stats
  const stats = {
      total: entries.length,
      completed: entries.filter(e => e.status === ProcessingStatus.COMPLETED).length,
      pending: entries.filter(e => e.status === ProcessingStatus.PENDING).length,
      review: entries.filter(e => e.status === ProcessingStatus.NEEDS_REVIEW).length
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white font-sans">
      
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-2 text-blue-500 mb-1">
            <Disc />
            <span className="font-bold text-lg text-white tracking-tight">DiscogsScan</span>
          </div>
          <p className="text-xs text-gray-500">Local Library Organizer</p>
        </div>

        <div className="p-6 space-y-6 flex-1 overflow-y-auto">
            
            {/* Settings */}
            <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <Settings className="w-3 h-3" /> API Configuration
                </label>
                <input 
                    type="password" 
                    placeholder="Paste Discogs Token" 
                    value={token}
                    onChange={(e) => saveToken(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-all"
                />
                <p className="text-[10px] text-gray-500">Required for search & rate limits.</p>
            </div>

            <hr className="border-gray-800" />

            {/* Actions */}
            <div className="space-y-3">
                <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 text-white py-3 px-4 rounded-lg transition-all border border-gray-700 group"
                >
                    <Folder className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
                    <span className="text-sm font-medium">Select Root Folder</span>
                </button>
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFolderSelect} 
                    className="hidden" 
                    // @ts-ignore - Standard React TS definitions miss webkitdirectory
                    webkitdirectory="" 
                    directory="" 
                    multiple 
                />

                <button 
                    onClick={startProcessing}
                    disabled={isProcessing || entries.length === 0 || !token}
                    className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg transition-all ${isProcessing || entries.length === 0 || !token ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20'}`}
                >
                    {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
                    <span className="text-sm font-medium">{isProcessing ? 'Scanning...' : 'Start Scan'}</span>
                </button>
            </div>

            {/* Stats */}
            {entries.length > 0 && (
                <div className="space-y-4 pt-4">
                    <h4 className="text-xs font-semibold text-gray-400 uppercase">Progress</h4>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-gray-800/50 p-3 rounded border border-gray-800">
                            <div className="text-2xl font-bold text-white">{stats.total}</div>
                            <div className="text-[10px] text-gray-400">Folders</div>
                        </div>
                        <div className="bg-green-900/20 p-3 rounded border border-green-900/30">
                            <div className="text-2xl font-bold text-green-400">{stats.completed}</div>
                            <div className="text-[10px] text-green-300/70">Matched</div>
                        </div>
                        <div className="bg-yellow-900/20 p-3 rounded border border-yellow-900/30">
                            <div className="text-2xl font-bold text-yellow-400">{stats.review}</div>
                            <div className="text-[10px] text-yellow-300/70">Conflicts</div>
                        </div>
                        <div className="bg-gray-800/50 p-3 rounded border border-gray-800">
                            <div className="text-2xl font-bold text-gray-400">{stats.pending}</div>
                            <div className="text-[10px] text-gray-500">Pending</div>
                        </div>
                    </div>
                </div>
            )}
        </div>

        <div className="p-6 border-t border-gray-800 mt-auto">
             <button 
                onClick={handleExport}
                disabled={stats.completed === 0}
                className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 disabled:bg-gray-800 disabled:text-gray-600 text-white py-2 px-4 rounded transition-colors"
             >
                 <Download className="w-4 h-4" />
                 <span className="text-sm font-medium">Export to CSV</span>
             </button>
             <p className="text-[10px] text-center text-gray-600 mt-3">
                Web-based simulation. Files are not modified on disk.
             </p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-gray-950 relative">
        {/* Header */}
        <header className="h-16 border-b border-gray-800 flex items-center justify-between px-8 bg-gray-900/50 backdrop-blur">
            <h1 className="text-xl font-medium text-white flex items-center gap-2">
                <ListMusic className="w-5 h-5 text-gray-400" />
                Library Queue
            </h1>
            {isProcessing && (
                 <div className="flex items-center gap-3 bg-blue-900/30 px-4 py-1.5 rounded-full border border-blue-800/50">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-blue-200">Processing item {processingIndex + 1} of {entries.length}</span>
                 </div>
            )}
        </header>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-8">
            {entries.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
                    <div className="w-20 h-20 bg-gray-900 rounded-full flex items-center justify-center border border-gray-800">
                        <FileUp className="w-8 h-8 text-gray-600" />
                    </div>
                    <p className="text-lg">No folders selected</p>
                    <p className="text-sm max-w-md text-center text-gray-600">Select a parent directory containing your music folders to begin analyzing.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {entries.map(entry => (
                        <AlbumCard 
                            key={entry.id} 
                            entry={entry} 
                            onReview={(e) => setResolvingEntry(e)}
                        />
                    ))}
                </div>
            )}
        </div>
      </main>

      {/* Modal */}
      {resolvingEntry && (
        <ConflictResolver 
            entry={resolvingEntry} 
            isOpen={!!resolvingEntry}
            onClose={() => setResolvingEntry(null)}
            onSelect={handleManualSelect}
        />
      )}
    </div>
  );
}