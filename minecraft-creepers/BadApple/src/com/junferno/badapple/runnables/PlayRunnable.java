package com.junferno.badapple.runnables;

import java.util.LinkedList;
import java.util.List;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.Enderman;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Monster;
import org.bukkit.entity.Player;
import org.bukkit.scheduler.BukkitRunnable;
import org.json.simple.JSONArray;

import com.junferno.badapple.BadApple;

public class PlayRunnable extends BukkitRunnable {

	protected JSONArray frames;

	private static final double RANGE = 100.0;

	private static int WIDTH;
	private static int HEIGHT;

	private static long ratio = 0;
	private static int countDown = 0;

	private static boolean day;

	public PlayRunnable(JSONArray frames) {
		super();
		this.frames = frames;
		WIDTH = ((JSONArray) (frames.get(0))).size();
		HEIGHT = ((JSONArray) ((JSONArray) (frames.get(0))).get(0)).size();
		day = true;
	}

//	public long geti (JSONArray frame, int i, int j) {
//		return (long) ((JSONArray) frame.get(i)).get(j);
//	}
	
//	class Coordinate {
//		
//		public int x;
//		public int z;
//		
//		public Coordinate(int x, int z) {
//			this.x = x;
//			this.z = z;
//		}
//	}

//	public Coordinate bfs(JSONArray frame, int x, int z) {
//		LinkedList<Integer> xq = new LinkedList<Integer>();
//		LinkedList<Integer> zq = new LinkedList<Integer>();
//
//		xq.add(x);
//		zq.add(z);
//
//		boolean [][] visited = new boolean[WIDTH][HEIGHT];
//
//		while (!xq.isEmpty()) {
//			int xc = xq.pop();
//			int zc = zq.pop();
//
//			visited[xc][zc] = true;
//
//			if (geti(frame, xc, zc) == 1) return new Coordinate(xc, zc);
//
//			if (xc-1 >= 0 && !visited[xc-1][zc]) {
//				xq.add(xc-1);
//				zq.add(zc);
//			}
//			if (xc+1 < WIDTH && !visited[xc+1][zc]) {
//				xq.add(xc+1);
//				zq.add(zc);
//			}
//			if (zc-1 >= 0 && !visited[xc][zc-1]) {
//				xq.add(xc);
//				zq.add(zc-1);
//			}
//			if (zc+1 >= 0 && !visited[xc][zc+1]) {
//				xq.add(xc);
//				zq.add(zc+1);
//			}
//
//		}
//
//		return null;
//
//	}

	@Override
	public void run(){

		BadApple.getPlayer().getLocation();

		if (BadApple.getStart() == -1)
			return;

		if (BadApple.index >= this.frames.size()) {
			BadApple.setStart(-1);
			BadApple.index = 0;
			return;
		}

		if (countDown > 0) {
			countDown--;
			return;
		}

		Player p = BadApple.getPlayer();
		
		if (p == null)
			return;

		if (day && p.getWorld().getTime() >= 13000) {
			day = false;
			for (int i=(int) BadApple.x; i!=(int)(BadApple.x + BadApple.width); i += (int)(BadApple.width/Math.abs(BadApple.width))) {
				for (int j=(int) BadApple.z; j!=(int)(BadApple.z + BadApple.height); j += (int)(BadApple.height/Math.abs(BadApple.height))) {
					for (int b=6; b<=18; b++) {
						Location back = new Location(p.getWorld(), i, BadApple.y-b, j);
						back.getBlock().setType(Material.GLOWSTONE);
					}
				}
			}
		}

		JSONArray frame = (JSONArray) this.frames.get(BadApple.index);
		boolean [][] visited = new boolean[WIDTH][HEIGHT];

		long prevRatio = ratio;
		ratio = 0;

		for (int i=0; i<WIDTH; i++)
			for (int j=0; j<HEIGHT; j++) {
				long state = (long) ((JSONArray) frame.get(i)).get(j);
				if (state == 0)
					ratio++;
				else if (state == 1)
					ratio--;
			}

		if (ratio != 0 && prevRatio != 0 && ratio/Math.abs(ratio) != prevRatio/Math.abs(prevRatio)) {
			Location l = new Location(p.getWorld(), BadApple.x + (Math.random()*BadApple.width), BadApple.y, BadApple.z + (Math.random()*BadApple.height));
			p.getWorld().strikeLightning(l);
		}

		List<LivingEntity> entities = p.getLocation().getWorld().getLivingEntities();
		for (Entity entity:entities)
			if (entity.getLocation().distance(p.getLocation()) <= BadApple.RANGE && entity instanceof Monster) {
				if (entity instanceof Creeper) {
					Creeper creeper = (Creeper) entity;
					Location l = creeper.getLocation();
					int i = WIDTH - (int) Math.abs((l.getX() - BadApple.x) * (WIDTH/BadApple.width));
					int j = (int) Math.abs((l.getZ() - BadApple.z) * (HEIGHT/BadApple.height));
					try {
						if (visited[i][j] || creeper.getLocation().getY() < BadApple.y) {
							creeper.remove();
							continue;
						}
						long state = (long) ((JSONArray) frame.get(i)).get(j);
						visited[i][j] = true;
						if (state == 0) creeper.explode();
					}
					catch (IndexOutOfBoundsException e) {
						creeper.remove();
						continue;
					}
				}
//				else if (entity instanceof Enderman) {
//					Enderman enderman = (Enderman) entity;
//					Location l = enderman.getLocation();
//					int i = WIDTH - (int) Math.abs((l.getX() - BadApple.x) * (WIDTH/BadApple.width));
//					int j = (int) Math.abs((l.getZ() - BadApple.z) * (HEIGHT/BadApple.height));
//					try {
//						long state = (long) ((JSONArray) frame.get(i)).get(j);
//						if (state == 0) {
//							Coordinate coord = bfs(frame, i, j);
//							
//							if (coord == null)
//								enderman.remove();
//							else {
//								visited[coord.x][coord.z] = true; 
//								Location newl = new Location(p.getWorld(), 
//										BadApple.x + (WIDTH - coord.x) * (BadApple.width/WIDTH), 
//										BadApple.y, 
//										BadApple.z + coord.z * (BadApple.height/HEIGHT));
//								enderman.teleport(newl);
//							}
//						}
//					}
//					catch (IndexOutOfBoundsException e) {
//						enderman.remove();
//						continue;
//					}
//
//				}
			}

		if (BadApple.getStart() == 1)
			for (int i=(int) BadApple.x; i!=(int)(BadApple.x + BadApple.width); i += (int)(BadApple.width/Math.abs(BadApple.width))) {
				for (int j=(int) BadApple.z; j!=(int)(BadApple.z + BadApple.height); j += (int)(BadApple.height/Math.abs(BadApple.height))) {
					int x = WIDTH - (int) Math.abs((i - BadApple.x) * (WIDTH/BadApple.width));
					int z = (int) Math.abs((j - BadApple.z) * (HEIGHT/BadApple.height));
					try {
						if ((long) ((JSONArray) frame.get(x)).get(z) == 1 && !visited[x][z]) {
							Location l = new Location(BadApple.getPlayer().getWorld(), i, BadApple.y, j);
							Location support = new Location(BadApple.getPlayer().getWorld(), i, BadApple.y-1, j);
							support.getBlock().setType(Material.BLACK_WOOL);
							BadApple.getPlayer().getWorld().spawnEntity(l, EntityType.CREEPER);
						}
					}
					catch (IndexOutOfBoundsException e) {

					}
				}
			}
//		else if (BadApple.getStart() == 2)
//			for (int i=(int) BadApple.x; i!=(int)(BadApple.x + BadApple.width); i += (int)(BadApple.width/Math.abs(BadApple.width))) {
//				for (int j=(int) BadApple.z; j!=(int)(BadApple.z + BadApple.height); j += (int)(BadApple.height/Math.abs(BadApple.height))) {
//					int x = WIDTH - (int) Math.abs((i - BadApple.x) * (WIDTH/BadApple.width));
//					int z = (int) Math.abs((j - BadApple.z) * (HEIGHT/BadApple.height));
//					try {
//						if ((long) ((JSONArray) frame.get(x)).get(z) == 1 && !visited[x][z]) {
//							Location l = new Location(BadApple.getPlayer().getWorld(), i, BadApple.y, j);
//							BadApple.getPlayer().getWorld().spawnEntity(l, EntityType.ENDERMAN);
//						}
//					}
//					catch (IndexOutOfBoundsException e) {
//
//					}
//				}
//			}
			

		BadApple.index++;

	}

}

