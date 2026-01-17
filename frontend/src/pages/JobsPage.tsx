import { useEffect, useState } from 'react';
import { jobsApi, profilesApi, contentApi, Job, Profile } from '../api/client';

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [showNewJob, setShowNewJob] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      loadJobs(selectedProfile);
    }
  }, [selectedProfile]);

  const loadData = async () => {
    try {
      const profilesRes = await profilesApi.list();
      setProfiles(profilesRes.data);
      if (profilesRes.data.length > 0) {
        setSelectedProfile(profilesRes.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadJobs = async (profileId: string) => {
    try {
      const res = await jobsApi.list({ profile_id: profileId });
      setJobs(res.data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const handleCreateJob = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      await jobsApi.create({
        profile_id: selectedProfile,
        title: formData.get('title') as string,
        company_name: formData.get('company_name') as string,
        description: formData.get('description') as string,
        url: formData.get('url') as string,
        location: formData.get('location') as string,
        source: 'manual',
        status: 'interested',
      });

      setShowNewJob(false);
      loadJobs(selectedProfile);
    } catch (error) {
      console.error('Failed to create job:', error);
    }
  };

  const handleStatusChange = async (jobId: string, newStatus: string) => {
    try {
      await jobsApi.update(jobId, { status: newStatus as any });
      loadJobs(selectedProfile);
    } catch (error) {
      console.error('Failed to update job:', error);
    }
  };

  const handleGenerateContent = async (job: Job) => {
    try {
      setGeneratedContent(null);
      const res = await contentApi.generateContent({
        job_id: job.id,
        profile_id: selectedProfile,
      });
      setGeneratedContent(res.data);
      setSelectedJob(job);
    } catch (error) {
      console.error('Failed to generate content:', error);
      alert('Failed to generate content');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  const statusColors: Record<string, string> = {
    interested: 'bg-gray-100 text-gray-800',
    applied: 'bg-blue-100 text-blue-800',
    interviewing: 'bg-yellow-100 text-yellow-800',
    rejected: 'bg-red-100 text-red-800',
    offered: 'bg-green-100 text-green-800',
  };

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Jobs</h1>
        <div className="flex gap-4">
          <select
            value={selectedProfile}
            onChange={(e) => setSelectedProfile(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => setShowNewJob(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add Job
          </button>
        </div>
      </div>

      {showNewJob && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Add New Job</h2>
          <form onSubmit={handleCreateJob} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Job Title</label>
                <input
                  type="text"
                  name="title"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Company Name</label>
                <input
                  type="text"
                  name="company_name"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Location</label>
                <input
                  type="text"
                  name="location"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Job URL</label>
                <input
                  type="url"
                  name="url"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                name="description"
                rows={4}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Job
              </button>
              <button
                type="button"
                onClick={() => setShowNewJob(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{job.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{job.company_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{job.location || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={job.status}
                      onChange={(e) => handleStatusChange(job.id, e.target.value)}
                      className={`px-2 py-1 text-xs rounded-full ${statusColors[job.status]}`}
                    >
                      <option value="interested">Interested</option>
                      <option value="applied">Applied</option>
                      <option value="interviewing">Interviewing</option>
                      <option value="rejected">Rejected</option>
                      <option value="offered">Offered</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => handleGenerateContent(job)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Generate Content
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {generatedContent && selectedJob && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">
            Generated Content for {selectedJob.title}
          </h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-2">Cover Letter</h3>
              <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap">
                {generatedContent.cover_letter}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Outreach Emails</h3>
              <div className="space-y-4">
                {generatedContent.outreach_emails?.map((email: any, idx: number) => (
                  <div key={idx} className="border border-gray-200 rounded p-4">
                    <p className="text-sm font-medium text-gray-700">To: {email.recipient}</p>
                    <p className="text-sm font-medium text-gray-700 mt-1">
                      Subject: {email.subject}
                    </p>
                    <div className="mt-2 text-sm text-gray-600 whitespace-pre-wrap">
                      {email.body}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Application Strategy</h3>
              <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap">
                {generatedContent.application_strategy}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
