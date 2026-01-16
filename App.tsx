import React, { useState, useRef } from 'react';
import { Platform, AlbumResolution } from './types';
import { editImageWithGemini } from './services/geminiService';
import { Spinner } from './components/Spinner';

const App: React.FC = () => {
  // State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [platform, setPlatform] = useState<Platform>(Platform.INSTAGRAM);
  const [resolution, setResolution] = useState<AlbumResolution>(AlbumResolution.DISTRO);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setGeneratedImage(null); // Reset result on new upload
      setError(null);
    }
  };

  const handleGenerate = async () => {
    if (!selectedFile) {
      setError("Please upload an image first.");
      return;
    }
    // Prompt is now optional, removed validation check

    setIsGenerating(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const resultUrl = await editImageWithGemini(selectedFile, prompt, platform, resolution);
      setGeneratedImage(resultUrl);
    } catch (err: any) {
      setError(err.message || "Failed to generate image. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadImage = () => {
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = `visual-adapt-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 selection:bg-indigo-500/30">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-violet-400">
              VisualAdapt AI
            </h1>
          </div>
          <div className="text-xs font-mono text-zinc-500">
            Powered by Gemini 2.5
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Controls */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Upload Section */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">1. Source Image</h2>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="relative group cursor-pointer border-2 border-dashed border-zinc-700 hover:border-indigo-500 rounded-xl p-8 transition-all duration-300 flex flex-col items-center justify-center bg-zinc-900/30 hover:bg-zinc-800/50"
            >
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleFileChange} 
                accept="image/*" 
                className="hidden" 
              />
              
              {previewUrl ? (
                <div className="relative w-full aspect-video md:aspect-square bg-black rounded-lg overflow-hidden">
                  <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <span className="text-white text-sm font-medium">Change Image</span>
                  </div>
                </div>
              ) : (
                <>
                  <svg className="w-10 h-10 text-zinc-500 mb-3 group-hover:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-sm text-zinc-400 text-center">Click to upload or drag and drop</p>
                  <p className="text-xs text-zinc-600 mt-1">JPG, PNG up to 10MB</p>
                </>
              )}
            </div>
          </section>

          {/* Settings Section */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">2. Configuration</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1.5">Target Platform</label>
                <select 
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value as Platform)}
                  className="w-full bg-black border border-zinc-700 text-zinc-200 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5"
                >
                  {Object.values(Platform).map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              {platform === Platform.ALBUM_COVER && (
                <div className="animate-fade-in-down">
                  <label className="block text-xs font-medium text-indigo-300 mb-1.5">Resolution (Upscale Target)</label>
                  <select 
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value as AlbumResolution)}
                    className="w-full bg-indigo-950/30 border border-indigo-500/30 text-indigo-100 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5"
                  >
                    {Object.values(AlbumResolution).map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1.5">Instruction (Optional)</label>
                <textarea 
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe desired changes, or leave empty for auto-adaptation..."
                  className="w-full bg-black border border-zinc-700 text-zinc-200 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-3 min-h-[100px] resize-none"
                />
                <p className="text-xs text-zinc-500 mt-1">
                  Describe the changes or style you want.
                </p>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !selectedFile}
              className={`mt-6 w-full flex items-center justify-center gap-2 text-white font-medium rounded-xl text-sm px-5 py-3 transition-all ${
                isGenerating || !selectedFile
                  ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 active:scale-[0.98]'
              }`}
            >
              {isGenerating ? (
                <>
                  <Spinner />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Generate Adaptation</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </>
              )}
            </button>
            
            {error && (
              <div className="mt-4 p-3 bg-red-950/30 border border-red-900/50 rounded-lg text-red-200 text-xs">
                {error}
              </div>
            )}
          </section>

        </div>

        {/* Right Column: Output */}
        <div className="lg:col-span-8 flex flex-col h-full min-h-[500px]">
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl flex-1 p-1 overflow-hidden relative flex flex-col">
             <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
             
             {generatedImage ? (
               <div className="flex-1 flex flex-col items-center justify-center bg-black/50 rounded-xl relative p-4 md:p-8 overflow-auto">
                 <img 
                   src={generatedImage} 
                   alt="Generated Result" 
                   className="max-w-full max-h-[70vh] object-contain shadow-2xl rounded-md ring-1 ring-white/10" 
                 />
                 <div className="absolute bottom-4 right-4 flex gap-2">
                    <button 
                      onClick={downloadImage}
                      className="bg-white text-black hover:bg-zinc-200 font-medium rounded-lg text-sm px-4 py-2 shadow-xl flex items-center gap-2 transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download
                    </button>
                 </div>
               </div>
             ) : (
               <div className="flex-1 flex flex-col items-center justify-center text-zinc-600">
                 {isGenerating ? (
                   <div className="text-center space-y-4">
                     <div className="inline-block p-4 rounded-full bg-indigo-500/10 animate-pulse">
                        <svg className="w-8 h-8 text-indigo-500 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                     </div>
                     <p className="text-sm font-medium text-zinc-400">AI is reimaging your visual...</p>
                     <p className="text-xs text-zinc-600">This might take a few seconds</p>
                   </div>
                 ) : (
                   <>
                     <svg className="w-16 h-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                     </svg>
                     <p className="text-sm">Generated artwork will appear here</p>
                   </>
                 )}
               </div>
             )}
          </section>
        </div>
      </main>
    </div>
  );
};

export default App;