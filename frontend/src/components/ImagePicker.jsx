import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Search, Loader2, Image as ImageIcon } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ImagePicker = ({ isOpen, onClose, onSelectImage }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [uploading, setUploading] = useState(false);

    // Load curated images on mount
    useEffect(() => {
        if (isOpen && images.length === 0) {
            loadCuratedImages();
        }
    }, [isOpen]);

    const loadCuratedImages = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`${BACKEND_URL}/api/images/curated`, {
                params: { per_page: 15, page: 1 }
            });
            setImages(response.data.photos || []);
            setPage(1);
        } catch (err) {
            console.error('Error loading curated images:', err);
            setError('Failed to load images. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`${BACKEND_URL}/api/images/search`, {
                params: { query: searchQuery, per_page: 15, page: 1 }
            });
            setImages(response.data.photos || []);
            setPage(1);
        } catch (err) {
            console.error('Error searching images:', err);
            setError('Failed to search images. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleImageSelect = (image) => {
        // Pass the medium-sized image URL and photographer info
        onSelectImage({
            url: image.src.large,
            photographer: image.photographer,
            photographer_url: image.photographer_url,
            alt: image.alt || searchQuery || 'Image from Pexels'
        });
        onClose();
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Check file type
        if (!file.type.startsWith('image/')) {
            setError('Please select an image file');
            return;
        }

        setUploading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(
                `${BACKEND_URL}/api/upload-image`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            // Use the uploaded image
            onSelectImage({
                url: response.data.url,
                alt: file.name,
                photographer: 'User Upload',
                photographer_url: ''
            });

        } catch (err) {
            console.error('Upload failed:', err);
            setError('Failed to upload image. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
                <DialogHeader>
                    <DialogTitle>Insert Image</DialogTitle>
                </DialogHeader>

                {/* Upload Button */}
                <div className="border-b pb-3">
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        id="image-upload-input"
                        disabled={uploading}
                    />
                    <label htmlFor="image-upload-input">
                        <Button
                            type="button"
                            variant="outline"
                            className="w-full cursor-pointer"
                            disabled={uploading}
                            onClick={(e) => {
                                e.preventDefault();
                                document.getElementById('image-upload-input').click();
                            }}
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <ImageIcon className="h-4 w-4 mr-2" />
                                    Upload from Computer
                                </>
                            )}
                        </Button>
                    </label>
                    <p className="text-xs text-gray-500 mt-2 text-center">Or search Pexels below</p>
                </div>

                {/* Search Form */}
                <form onSubmit={handleSearch} className="flex gap-2">
                    <Input
                        type="text"
                        placeholder="Search for images..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1"
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                        Search
                    </Button>
                </form>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                        {error}
                    </div>
                )}

                {/* Images Grid */}
                <div className="flex-1 overflow-y-auto">
                    {loading && images.length === 0 ? (
                        <div className="flex items-center justify-center h-64">
                            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                        </div>
                    ) : images.length > 0 ? (
                        <div className="grid grid-cols-3 gap-4 p-2">
                            {images.map((image) => (
                                <div
                                    key={image.id}
                                    className="relative group cursor-pointer rounded-lg overflow-hidden aspect-square bg-gray-100"
                                    onClick={() => handleImageSelect(image)}
                                >
                                    <img
                                        src={image.src.medium}
                                        alt={image.alt || 'Pexels image'}
                                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                                    />
                                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-end p-2">
                                        <div className="text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                                            Photo by {image.photographer}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                            <ImageIcon className="h-16 w-16 mb-4" />
                            <p>Search for images to get started</p>
                        </div>
                    )}
                </div>

                {/* Footer with Attribution */}
                <div className="text-xs text-gray-500 text-center pt-2 border-t">
                    Photos provided by <a href="https://www.pexels.com" target="_blank" rel="noopener noreferrer" className="underline">Pexels</a>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default ImagePicker;
