export enum Platform {
  INSTAGRAM = 'Instagram (1:1)',
  TIKTOK = 'TikTok (9:16)',
  YOUTUBE = 'YouTube (16:9)',
  XIAOHONGSHU = 'Xiaohongshu (3:4)',
  ALBUM_COVER = 'Album Cover (1:1)'
}

export enum AlbumResolution {
  STD = 'Standard (1400px)',
  HD = 'HD (1600px)',
  UHD = 'Ultra HD (1800px)',
  DISTRO = 'DistroKid/Spotify (3000px)'
}

export interface GenerationConfig {
  platform: Platform;
  resolution?: AlbumResolution;
  userPrompt: string;
  sourceImage: File | null;
}

export interface GeneratedResult {
  imageUrl: string;
  text?: string;
}
