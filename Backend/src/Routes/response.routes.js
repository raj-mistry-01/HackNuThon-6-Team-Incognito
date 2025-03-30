import express from "express";
import {
  addJsonToResponse,
  getTestResults,
  getResponse,
} from "../Controllers/reponse.controller.js";

const router = express.Router();

router.post("/add-json", addJsonToResponse);
router.post("/test-results", getTestResults);
router.post("/getResponse", getResponse);

export default router;