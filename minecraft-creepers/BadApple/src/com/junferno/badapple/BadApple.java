package com.junferno.badapple;

import java.nio.file.Paths;
import java.util.List;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Monster;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

import com.junferno.badapple.commands.EraseCommand;
import com.junferno.badapple.commands.InitCommand;
import com.junferno.badapple.commands.PlayCommand;
import com.junferno.badapple.commands.SetPlayerCommand;
import com.junferno.badapple.listeners.ExplosionListener;
import com.junferno.badapple.listeners.SpawnListener;
import com.junferno.badapple.runnables.PlayRunnable;
import com.junferno.badapple.utils.JSONHandler;

public class BadApple extends JavaPlugin {

	private static Player player = null;
	public static final double RANGE = 100D;
	private static int start = -1;

	public static double x = 0;
	public static double y = 0;
	public static double z = 0;
	
	public static double width = 54;
	public static double height = 72;
	
	public static int index = 0;

	private static int set = 0;

	private static JSONHandler json = new JSONHandler();

	public static Player getPlayer() {
		return player;
	}

	public static boolean isSelectedPlayer(Player p) {
		return p.equals(getPlayer());
	}

	public static boolean setPlayer(Player p) {
		if (p == null || p.isOnline()) {
			player = p;
			return true;
		}
		return false;
	}

	public static int getStart() {
		return BadApple.start;
	}

	public static void setStart(int value) {
		start = value;
		if (start == 2) {
			width = 27;
			height = 36;
		}
	}

	public static void setXY(double x, double y, double z) {
		BadApple.x = x;
		BadApple.y = y;
		BadApple.z = z;
		BadApple.set = Math.max(BadApple.set, 1);
	}

	public static boolean setWH(double x, double z) {
		if (BadApple.set < 1) return false;
		BadApple.width = x - BadApple.x;
		BadApple.height = z - BadApple.z;
		BadApple.set = 2;
		return true;
	}

	public static boolean spawnInit(EntityType eType, Material plat, Material backing) {
		System.out.println(BadApple.x + ", " + BadApple.y + ", " + BadApple.width + ", " + BadApple.height);
		if (BadApple.set < 1 || BadApple.player == null) return false;
		for (int i=(int) BadApple.x; i!=(int)(BadApple.x + BadApple.width); i += (int)(BadApple.width/Math.abs(BadApple.width))) {
			for (int j=(int) BadApple.z; j!=(int)(BadApple.z + BadApple.height); j += (int)(BadApple.height/Math.abs(BadApple.height))) {
				Location l = new Location(BadApple.player.getWorld(), i, BadApple.y, j);
				Location support = new Location(BadApple.player.getWorld(), i, BadApple.y-1, j);
				support.getBlock().setType(plat);
				if (backing != null)
					for (int b=6; b<=18; b++) {
						Location back = new Location(BadApple.player.getWorld(), i, BadApple.y-b, j);
						back.getBlock().setType(backing);
					}
				BadApple.player.getWorld().spawnEntity(l, eType);
			}
		}
		return true;
	}

	@SuppressWarnings("unchecked")
	@Override
	public void onEnable() {
		getServer().getPluginManager().registerEvents(new SpawnListener(), this);
		getServer().getPluginManager().registerEvents(new ExplosionListener(), this);
		
		new SetPlayerCommand(this);
		new PlayCommand(this);
		new EraseCommand(this);
		new InitCommand(this);

		new PlayRunnable(json.readJSONFileArray(Paths.get("plugins", "BadApple", "data.json").toString())).runTaskTimer(this, 0L, 4L);
	}

	@Override
	public void onDisable() {
		BadApple.setStart(-1);
		
		if (BadApple.getPlayer() == null) return;
		
		List<LivingEntity> entities = BadApple.getPlayer().getLocation().getWorld().getLivingEntities();
		for (Entity entity:entities)
			if (entity.getLocation().distance(BadApple.getPlayer().getLocation()) <= BadApple.RANGE && entity instanceof Monster) {
				if (entity instanceof Creeper) {
					Creeper creeper = (Creeper) entity;
					creeper.remove();
				}
			}
	}

}
