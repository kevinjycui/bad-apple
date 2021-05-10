package com.junferno.badapple.utils;

import java.io.FileReader;
import java.io.IOException;

import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class JSONHandler {
	
	private static JSONParser jsonParser = new JSONParser();
	protected JSONArray arr = null;
	
	public JSONArray readJSONFileArray(String filename) {
		try {
			JSONArray arr = (JSONArray) jsonParser.parse(new FileReader(filename));
			this.arr = arr;
			return arr;
		} catch (IOException | ParseException e) {
			e.printStackTrace();
		}
		return null;
	}
	
	public JSONArray readArrayIndex(int index) {
		if (this.arr == null)
			return null;
		if (index >= this.arr.size())
			return null;
		return (JSONArray) this.arr.get(index);
	}

}
