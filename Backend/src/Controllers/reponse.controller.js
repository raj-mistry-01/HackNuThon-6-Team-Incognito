// increase number of numOfTests and also add jsonObject

// in json object there exist test is pass or fails so return number of  pass and fails tests

// show all

// get responses

import {Response} from "../Models/Reponse.model.js";
import { Project } from "../Models/Project.model.js"

// Add JSON data to response.jsonobjects and update numOfTests
import multer from "multer";
import fs from "fs";
import os from "os"


// Multer configuration to handle JSON file uploads
const upload = multer({ dest: os.tmpdir() });

// Middleware to handle file upload
export const uploadJsonMiddleware = upload.single("jsonFile");

// Add JSON data to response.jsonobjects and update numOfTests
import mongoose from "mongoose";

export const addJsonToResponse = async (req, res) => {
  try {
    console.log("Received file:", req.file);
    console.log("Received body:", req.body);

    const { projectId } = req.body;

    if (!projectId || !req.file) {
      return res
        .status(400)
        .json({ error: "Project ID and JSON file are required" });
    }

    const jsonFilePath = req.file.path;
    console.log("JSON File Path:", jsonFilePath);

    let jsonData;
    try {
      jsonData = JSON.parse(fs.readFileSync(jsonFilePath, "utf-8"));
    } catch (err) {
      console.error("Error parsing JSON file:", err);
      return res.status(400).json({ error: "Invalid JSON file format" });
    }

    let responseDoc = await Response.findOne({ project: projectId });

    if (!responseDoc) {
      responseDoc = new Response({
        project: projectId,
        jsonobjects: [jsonData],
        numoftest: 0,
      });
    } else {
      responseDoc.jsonObjects.push(jsonData);
      responseDoc.numOfTests += 1;
    }

    await responseDoc.save();
    fs.unlinkSync(jsonFilePath);

    res.status(200).json({
      message: "JSON data added successfully",
      response: responseDoc,
    });
  } catch (error) {
    console.error("Error saving response to DB:", error);
    res.status(500).json({ error: "Failed to add JSON data" });
  }
};

// Get pass and fail test counts
export const getTestResults = async (req, res) => {
  try {
    const { projectId } = req.body;
    if (!projectId)
      return res.status(400).json({ error: "Project ID is required" });

    const responseDoc = await Response.findOne({ project: projectId });
    if (!responseDoc)
      return res.status(404).json({ error: "No test results found" });
    // console.log(responseDoc);
    const passedTests = responseDoc.jsonObjects.filter(
      (test) => test.passed_tests === "true"
    ).length;
    const failedTests = responseDoc.jsonObjects.filter(
      (test) => test.passed === "false"
    ).length;

    res.status(200).json({ passedTests, failedTests });
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch test results" });
  }
};

export const getResponse = async (req, res) => { 
    try {
        const { projectId } = req.body;
        if (!projectId)
        return res.status(400).json({ error: "Project ID is required" });
        const responseDoc = await Response.findOne({ project: projectId });
        if (!responseDoc)
        return res.status(404).json({ error: "No test results found" });
         res.status(200).json({ responseDoc });
    }
    catch (error) {
        res.status(500).json({ error: "Failed to fetch response" });
    }
}

// Get all responses
// export const getAllResponses = async (req, res) => {
//   try {
//     const responses = await Response.find().populate("project");
//     res.status(200).json(responses);
//   } catch (error) {
//     res.status(500).json({ error: "Failed to fetch responses" });
//   }
// };