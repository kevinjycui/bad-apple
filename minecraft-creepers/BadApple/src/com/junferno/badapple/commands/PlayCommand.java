package com.junferno.badapple.commands;

import org.bukkit.Material;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Player;

import com.junferno.badapple.BadApple;

public class PlayCommand implements CommandExecutor {
	
	private EntityType[] option1 = {EntityType.CREEPER, EntityType.ENDERMAN, EntityType.PIG};
	private Material[] option2 = {Material.BLACK_WOOL, Material.QUARTZ_BLOCK, Material.GRASS_BLOCK};
	private Material[] option3 = {Material.WHITE_WOOL, null, null};
	
	public PlayCommand(BadApple plugin) {
		plugin.getCommand("badapple").setExecutor(this);
	}

	@Override
	public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
		if (!(sender instanceof Player)) {
			sender.sendMessage("Only players may execute this command!");
			return false;
		}
		
		Player p = (Player) sender;
		
		if (args.length > 1) {
			p.sendMessage("Invalid number of arguments");
			return false;
		}
		
		try {
			int arg;
			if (args.length == 0)
				arg = 0;
			else
				arg = Integer.parseInt(args[0]) - 1;
			if (arg >= option1.length) throw new NumberFormatException();
			if (!BadApple.spawnInit(option1[arg], option2[arg], option3[arg])) {
				p.sendMessage("Error occurred while spawning entities");
				return false;
			}
			BadApple.setStart(arg + 1);
		}
		catch (NumberFormatException e) {
			p.sendMessage("Invalid argument " + args[0]);
			return false;
		}
		
		return true;
	}

}
