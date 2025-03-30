import mongoose, { Schema } from "mongoose";

const responseSchema = new Schema(
  {
    project: {
      type: Schema.Types.ObjectId,
      ref: "project"
    },
    numOfTests: {
      type: Number,
      default: 0,
    },
    jsonObjects: [
      {
        type: Schema.Types.Mixed, 
        required: true,
      },
    ],
  },
  {
    timestamps: true,
  }
);

export const Response = mongoose.model("Response", responseSchema);