package com.junferno.badapple.listeners;

import java.util.Collection;

import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;

import com.junferno.badapple.BadApple;

public class SpawnListener implements Listener {

	@EventHandler
	public void onJoin(PlayerJoinEvent event) {
		if (BadApple.getPlayer() == null && BadApple.setPlayer(event.getPlayer()))
			System.out.println("Player set to " + event.getPlayer().getDisplayName());
	}

	@EventHandler
	public void onLeave(PlayerQuitEvent event) {
		Player p = event.getPlayer();
		if (p.equals(BadApple.getPlayer())) {
			Collection<? extends Player> players = event.getPlayer().getServer().getOnlinePlayers();
			for (Player q:players)
				if (!p.equals(q)) {
					BadApple.setPlayer(q);
					p.sendMessage("Player " + p.getDisplayName() + " quit the game, player set to " + q.getDisplayName());
					System.out.println("Player " + p.getDisplayName() + " quit the game, player set to " + q.getDisplayName());
					return;
				}
			BadApple.setPlayer(null);
			p.sendMessage("Player " + p.getDisplayName() + " quit the game, there is no more player");
			System.out.println("Player " + p.getDisplayName() + " quit the game, there is no more player");
		}
	}

}
