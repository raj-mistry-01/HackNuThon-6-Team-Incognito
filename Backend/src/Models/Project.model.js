import mongoose from 'mongoose';

const projectSchema = new mongoose.Schema({
  owner: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  figmaFileId: {
    type: String,
    required: true,
    trim: true
  },
  figmaLink: {
    type: String,
    required: true,
    trim: true
  },
  gitlabLink: {
    type: String,
    trim: true,
    default: null
  },
  githubLink: {
    type: String,
    trim: true,
    default: null
  },
  websiteUrl: {
    type: String,
    trim: true,
    default: null
  },
  status: {
    type: String,
    enum: ['Planning', 'In Progress', 'Completed'],
    default: 'Planning'
  }
}, {
  timestamps: true
});

// ✅ Use export default syntax
const Project = mongoose.model('Project', projectSchema);
export default Project;
