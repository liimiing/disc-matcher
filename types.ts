export interface DiscogsRelease {
  id: number;
  title: string;
  year?: string;
  thumb?: string;
  cover_image?: string;
  country?: string;
  genre?: string[];
  style?: string[];
  label?: string[];
  catno?: string;
  format?: string[];
  uri?: string;
}

export interface DiscogsSearchResult {
  id: number;
  title: string; // Usually "Artist - Album"
  year?: string;
  thumb?: string;
  cover_image?: string;
  label?: string[];
  country?: string;
  catno?: string;
  genre?: string[];
  style?: string[];
  format?: string[];
}

export enum ProcessingStatus {
  PENDING = 'PENDING',
  SEARCHING = 'SEARCHING',
  NEEDS_REVIEW = 'NEEDS_REVIEW', // Multiple matches or low confidence
  COMPLETED = 'COMPLETED',
  NOT_FOUND = 'NOT_FOUND',
  ERROR = 'ERROR'
}

export interface AlbumEntry {
  id: string; // Unique ID (folder path)
  folderName: string; // The specific album folder name
  fullPath: string; // Full relative path
  status: ProcessingStatus;
  searchResults: DiscogsSearchResult[];
  selectedRelease: DiscogsSearchResult | null;
  aiAnalysis?: string; // Creative: AI generated mood/description
  files: string[]; // List of files in folder
}

export interface GlobalSettings {
  discogsToken: string;
}