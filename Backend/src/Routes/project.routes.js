import express from "express";
import {
  getUserProjects,
  addUserProject,
  getProjectById,
  deleteProject,
} from "../Controllers/projects.controller.js";

const router = express.Router();

router.post("/getprojects", getUserProjects); // Get all projects for a user
router.post("/adduserproject", addUserProject); // Add a new project
router.get("/:id", getProjectById); // Get a single project by ID
// router.put("/:id", updateProject); // Update a project
router.delete("/:id", deleteProject); // Delete a project
1
export default router;