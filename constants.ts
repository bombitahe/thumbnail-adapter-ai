import { Platform, AlbumResolution } from './types';

export const MODEL_NAME = 'gemini-2.5-flash-image';

export const ASPECT_RATIOS: Record<Platform, string> = {
  [Platform.INSTAGRAM]: '1:1',
  [Platform.TIKTOK]: '9:16',
  [Platform.YOUTUBE]: '16:9',
  [Platform.XIAOHONGSHU]: '3:4',
  [Platform.ALBUM_COVER]: '1:1',
};

// Logic for specialized prompts based on the persona
export const getSystemPromptAugmentation = (platform: Platform, resolution?: AlbumResolution): string => {
  let prompt = '';

  if (platform === Platform.TIKTOK) {
    prompt += `
    \n*** RE-LAYOUT INSTRUCTIONS (9:16) ***
    Recompose this image into a vertical 9:16 format. DO NOT just extend borders.
    1. Identify and separate the text layer and the main subject.
    2. Move the Title/Text to the upper empty space (top 1/3), make it large and legible.
    3. Move the Main Subject to the center or lower 2/3 and scale it up to fill the width.
    4. Regenerate the background behind moved elements seamlessly.
    The result should look like a native TikTok poster.
    `;
  } else if (platform === Platform.ALBUM_COVER) {
    const resValue = resolution ? resolution.split('(')[1].replace(')', '') : '3000px';
    prompt += `
    \n*** ALBUM COVER SPECS ***
    Target Resolution Goal: ${resValue}.
    Ensure maximum fidelity, crisp text, and artistic composition suitable for music streaming platforms.
    Upscale and Denoise if necessary to meet high-quality standards.
    `;
  } else if (platform === Platform.XIAOHONGSHU) {
    prompt += `
    \n*** XIAOHONGSHU FORMAT (3:4) ***
    Ensure the composition is balanced vertically. Maintain a lifestyle aesthetic.
    `;
  }

  return prompt;
};
