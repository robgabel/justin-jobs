import { useEffect, useState } from 'react';
import { profilesApi, starAnswersApi, Profile, STARAnswer } from '../api/client';

export default function ProfilePage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [starAnswers, setStarAnswers] = useState<STARAnswer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewProfile, setShowNewProfile] = useState(false);
  const [showProfileBuilder, setShowProfileBuilder] = useState(false);
  const [builderResponse, setBuilderResponse] = useState('');
  const [builderQuestions, setBuilderQuestions] = useState<string[]>([]);

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      loadStarAnswers(selectedProfile.id);
    }
  }, [selectedProfile]);

  const loadProfiles = async () => {
    try {
      const res = await profilesApi.list();
      setProfiles(res.data);
      if (res.data.length > 0 && !selectedProfile) {
        setSelectedProfile(res.data[0]);
      }
    } catch (error) {
      console.error('Failed to load profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStarAnswers = async (profileId: string) => {
    try {
      const res = await starAnswersApi.list(profileId);
      setStarAnswers(res.data);
    } catch (error) {
      console.error('Failed to load STAR answers:', error);
    }
  };

  const handleCreateProfile = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      const res = await profilesApi.create({
        name: formData.get('name') as string,
        email: formData.get('email') as string,
        interests: [],
        strengths: [],
        weaknesses: [],
      });

      setProfiles([...profiles, res.data]);
      setSelectedProfile(res.data);
      setShowNewProfile(false);
    } catch (error) {
      console.error('Failed to create profile:', error);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !selectedProfile) return;

    const file = e.target.files[0];
    try {
      await profilesApi.uploadResume(selectedProfile.id, file);
      alert('Resume uploaded successfully!');
      loadProfiles();
    } catch (error) {
      console.error('Failed to upload resume:', error);
      alert('Failed to upload resume');
    }
  };

  const handleStartProfileBuilder = async () => {
    if (!selectedProfile) return;

    setShowProfileBuilder(true);
    try {
      const res = await profilesApi.buildProfile(selectedProfile.id, {
        resume_text: selectedProfile.resume_text,
      });

      setBuilderQuestions(res.data.questions || []);
    } catch (error) {
      console.error('Failed to start profile builder:', error);
    }
  };

  const handleSubmitBuilderResponse = async () => {
    if (!selectedProfile || !builderResponse) return;

    try {
      const res = await profilesApi.buildProfile(selectedProfile.id, {
        user_response: builderResponse,
      });

      setBuilderQuestions(res.data.questions || []);
      setBuilderResponse('');

      if (res.data.completed) {
        alert('Profile building complete!');
        setShowProfileBuilder(false);
        loadProfiles();
      }
    } catch (error) {
      console.error('Failed to submit response:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <button
          onClick={() => setShowNewProfile(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          New Profile
        </button>
      </div>

      {showNewProfile && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Create New Profile</h2>
          <form onSubmit={handleCreateProfile} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                name="name"
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                name="email"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowNewProfile(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {profiles.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No profiles yet. Create one to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold">Profiles</h2>
              </div>
              <div className="divide-y">
                {profiles.map((profile) => (
                  <div
                    key={profile.id}
                    onClick={() => setSelectedProfile(profile)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedProfile?.id === profile.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <h3 className="font-medium">{profile.name}</h3>
                    <p className="text-sm text-gray-500">{profile.email}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {selectedProfile && (
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-xl font-semibold mb-4">{selectedProfile.name}</h2>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Resume
                      </label>
                      {selectedProfile.resume_text ? (
                        <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded max-h-40 overflow-y-auto">
                          {selectedProfile.resume_text.substring(0, 500)}...
                        </div>
                      ) : (
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                          <input
                            type="file"
                            accept=".pdf,.txt"
                            onChange={handleFileUpload}
                            className="hidden"
                            id="resume-upload"
                          />
                          <label
                            htmlFor="resume-upload"
                            className="cursor-pointer text-blue-600 hover:text-blue-700"
                          >
                            Upload Resume (PDF or TXT)
                          </label>
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Interests</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedProfile.interests.map((interest, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                          >
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Strengths</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedProfile.strengths.map((strength, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                          >
                            {strength}
                          </span>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleStartProfileBuilder}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Build Profile with AI
                    </button>
                  </div>
                </div>

                {showProfileBuilder && (
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Profile Builder</h3>
                    {builderQuestions.length > 0 && (
                      <div className="space-y-4">
                        <div className="bg-blue-50 p-4 rounded">
                          {builderQuestions.map((question, idx) => (
                            <p key={idx} className="text-sm text-gray-700 mb-2">
                              {idx + 1}. {question}
                            </p>
                          ))}
                        </div>
                        <textarea
                          value={builderResponse}
                          onChange={(e) => setBuilderResponse(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                          rows={6}
                          placeholder="Type your answers here..."
                        />
                        <button
                          onClick={handleSubmitBuilderResponse}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          Submit Response
                        </button>
                      </div>
                    )}
                  </div>
                )}

                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-semibold mb-4">STAR Stories</h3>
                  {starAnswers.length === 0 ? (
                    <p className="text-sm text-gray-500">
                      No STAR stories yet. Add them to showcase your experiences.
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {starAnswers.map((star) => (
                        <div key={star.id} className="border-l-4 border-blue-500 pl-4">
                          <p className="text-sm font-medium text-gray-700">Situation: {star.situation}</p>
                          <p className="text-sm text-gray-600 mt-1">Result: {star.result}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
