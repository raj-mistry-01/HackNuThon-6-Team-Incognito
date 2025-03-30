import mongoose, { Schema } from "mongoose";

const projectSchema = new Schema(
  {
    owner: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    figmaFileId: {
      type: String,
      required: true,
      trim: true,
    },
    figmaLink: {
      type: String,
      required: true,
      trim: true,
    },
    gitlabLink: {
      type: String,
      trim: true,
      default: null,
    },
    githubLink: {
      type: String,
      trim: true,
      default: null,
    },
    websiteUrl: {
      type: String,
      trim: true,
      default: null,
    },
    status: {
      type: String,
      enum: ["Planning", "In Progress", "Completed"],
      default: "Planning",
    },
  },
  {
    timestamps: true,
  }
);

export const Project  = mongoose.model("Project", projectSchema);