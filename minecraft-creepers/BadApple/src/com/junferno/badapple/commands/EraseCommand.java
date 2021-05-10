package com.junferno.badapple.commands;

import java.util.List;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Monster;
import org.bukkit.entity.Player;

import com.junferno.badapple.BadApple;

public class EraseCommand implements CommandExecutor {
		
	public EraseCommand(BadApple plugin) {
		plugin.getCommand("erase").setExecutor(this);
	}

	@Override
	public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
		if (!(sender instanceof Player)) {
			sender.sendMessage("Only players may execute this command!");
			return false;
		}
		
		Player p = (Player) sender;
		
		if (args.length > 0) {
			p.sendMessage("Invalid number of arguments");
			return false;
		}
		
		BadApple.setStart(-1);
		BadApple.index = 0;
		
		List<LivingEntity> entities = p.getLocation().getWorld().getLivingEntities();
		for (Entity entity:entities)
			if (entity.getLocation().distance(p.getLocation()) <= BadApple.RANGE)
				entity.remove();
		
		return true;
	}

}
