import { Project } from "../Models/Project.model.js"
import { User } from "../Models/User.model.js";
const getUserProjects = async (req, res) => {
    try {
        const userEmail = req.body.email;
        if (!userEmail)
            return res.status(400).json({ error: "User email is required" });

        const user = await User.findOne({ email: userEmail });
        if (!user) return res.status(404).json({ error: "User not found" });

        const projects = await Project.find({ owner: user._id });
        res.status(200).json(projects);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch projects" });
    }
};

const addUserProject = async (req, res) => {
    try {
        console.log("✅ Received Request");

        // ✅ Use correct syntax to extract email
        const userEmail = req.body.email;

        console.log("User Email:", userEmail);
        console.log("Request Body:", req.body);

        if (!userEmail) {
            return res.status(400).json({ error: "User email is required" });
        }

        // ✅ Find user by email
        const user = await User.findOne({ email: userEmail });

        if (!user) {
            return res.status(404).json({ error: "User not found" });
        }

        // ✅ Extract the project details from req.body
        const {
            title,
            figmaFileId,
            figmaLink,
            gitlabLink,
            githubLink,
            websiteUrl,
            status
        } = req.body;

        // ✅ Create the new project
        const newProject = new Project({
            owner: user._id,
            title,
            figmaFileId,
            figmaLink,
            gitlabLink,
            githubLink,
            websiteUrl,
            status,
        });

        // ✅ Save the project
        await newProject.save();

        res.status(201).json(newProject);

    } catch (error) {
        console.error("🔥 Error:", error);
        res.status(500).json({ error: "Failed to add project" });
    }
};


// Get a single project by ID
const getProjectById = async (req, res) => {
    try {
        console.log("yes")
        console.log(req.params.id)
        const project = await Project.findById(req.params.id);
        if (!project) return res.status(404).json({ error: "Project not found" });
        res.status(200).json(project);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch project" });
    }
};

// // Update a project
// export const updateProject = async (req, res) => {
//   try {
//     const updatedProject = await Project.findByIdAndUpdate(
//       req.params.id,
//       req.body,
//       { new: true }
//     );
//     if (!updatedProject)
//       return res.status(404).json({ error: "Project not found" });
//     res.status(200).json(updatedProject);
//   } catch (error) {
//     res.status(500).json({ error: "Failed to update project" });
//   }
// };

// Delete a project
const deleteProject = async (req, res) => {
    try {
        const deletedProject = await Project.findByIdAndDelete(req.params.id);
        if (!deletedProject)
            return res.status(404).json({ error: "Project not found" });
        res.status(200).json({ message: "Project deleted successfully" });
    } catch (error) {
        res.status(500).json({ error: "Failed to delete project" });
    }
};

export { getUserProjects, addUserProject, getProjectById, deleteProject };