import { GoogleGenAI } from "@google/genai";
import { Platform, AlbumResolution } from '../types';
import { MODEL_NAME, ASPECT_RATIOS, getSystemPromptAugmentation } from '../constants';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      } else {
        reject(new Error('Failed to convert file to base64'));
      }
    };
    reader.onerror = error => reject(error);
  });
};

export const editImageWithGemini = async (
  imageFile: File,
  userPrompt: string,
  platform: Platform,
  resolution?: AlbumResolution
): Promise<string> => {
  try {
    const base64Data = await fileToBase64(imageFile);
    const mimeType = imageFile.type;
    
    // Construct the full prompt
    // If userPrompt is empty, provide a strong default for adaptation
    const effectiveUserPrompt = userPrompt.trim() 
      ? userPrompt 
      : "Adapt this image to the target aspect ratio. Preserve the main subject, style, and aesthetics. Extend the background seamlessly if needed to fill the space.";

    const augmentation = getSystemPromptAugmentation(platform, resolution);
    const fullPrompt = `
      Task: Image Editing / Recomposition.
      User Instruction: ${effectiveUserPrompt}
      
      ${augmentation}
      
      Return ONLY the generated image.
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: {
        parts: [
          {
            inlineData: {
              data: base64Data,
              mimeType: mimeType,
            },
          },
          {
            text: fullPrompt,
          },
        ],
      },
      config: {
        imageConfig: {
          aspectRatio: ASPECT_RATIOS[platform],
        }
      }
    });

    // Extract image
    // Note: The response for gemini-2.5-flash-image might contain text or inlineData.
    // We iterate to find the inlineData.
    const candidates = response.candidates;
    if (!candidates || candidates.length === 0) {
      throw new Error("No candidates returned");
    }

    const parts = candidates[0].content.parts;
    let generatedImageUrl = '';

    for (const part of parts) {
      if (part.inlineData) {
        const base64String = part.inlineData.data;
        // Assume PNG if not specified, but typically the model returns standard formats.
        // We can try to guess or just use image/png as safe default for display
        generatedImageUrl = `data:image/png;base64,${base64String}`;
        break;
      }
    }

    if (!generatedImageUrl) {
       // Fallback check if it returned a text saying it can't do it, etc.
       const textPart = parts.find(p => p.text);
       if (textPart) {
         throw new Error(`Model returned text instead of image: ${textPart.text}`);
       }
       throw new Error("No image data found in response");
    }

    return generatedImageUrl;

  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};