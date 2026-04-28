import { useEffect, useRef, useState } from 'react';
import { FileText, MoreVertical, UploadCloud } from 'lucide-react';
import { API_BASE_URL } from '../shared/config/api';
import { useT } from '../shared/i18n/language-context';
import { formatFileSize } from '../shared/utils/format';
import { buildAuthHeaders, fetchJSON } from '../shared/utils/http';

export default function UploadView({ authToken }) {
  const t = useT();
  const fileInputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadFiles = async () => {
    if (!authToken) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchJSON(`${API_BASE_URL}/api/files?limit=20`, {
        headers: buildAuthHeaders(authToken),
      });
      setFiles(data?.items || []);
    } catch (err) {
      setError(err.message || 'failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [authToken]);

  const handlePickFile = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const selected = event.target.files?.[0];
    if (!selected || !authToken) return;
    const formData = new FormData();
    formData.append('file', selected);
    formData.append('parse', 'true');
    setUploading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
        method: 'POST',
        headers: buildAuthHeaders(authToken),
        body: formData,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.error || 'Upload failed');
      }
      await loadFiles();
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      event.target.value = '';
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
      <h2 className="text-xl font-bold text-gray-800 mb-6">{t.upload_title}</h2>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="border-2 border-dashed border-gray-300 rounded-2xl bg-gray-50 p-12 text-center hover:bg-blue-50 hover:border-blue-400 transition-colors cursor-pointer mb-8" onClick={handlePickFile}>
        <div className="bg-white w-16 h-16 rounded-full shadow-sm flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8 text-blue-500" />
        </div>
        <h3 className="text-lg font-medium text-gray-800 mb-2">{t.upload_drag}</h3>
        <p className="text-sm text-gray-500 mb-4">{t.upload_formats}</p>
        <button type="button" className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
          {uploading ? t.fetching_rate : t.browse}
        </button>
      </div>

      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-4">{t.recent_uploads}</h3>
        <div className="space-y-3">
          {loading ? <div className="text-sm text-gray-500">{t.fetching_rate}</div> : null}
          {!loading && files.length === 0 ? <div className="text-sm text-gray-400">No files yet.</div> : null}
          {files.map((file, i) => {
            const parseStatus = String(file.parse_status || '').toUpperCase();
            const done = parseStatus === 'SUCCESS';
            return (
              <div key={file.id || i} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:shadow-sm transition-shadow">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <FileText className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <div className="font-medium text-sm text-gray-800">{file.file_name}</div>
                    <div className="text-xs text-gray-500">{formatFileSize(file.file_size)} • {file.upload_time}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  {done ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {t.verified}
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      {t.ai_processing}
                    </span>
                  )}
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        {error ? <p className="text-xs text-amber-600 mt-3">{error}</p> : null}
      </div>
    </div>
  );
}
