Hooks:PreHook(PlayerDamage, "damage_bullet", "DamageTriggerOnBullet", function(self, attack_data)
    log("[Damage Trigger] Bullet damage detected.")

    log("[Damage Trigger] Attack data: " .. tostring(attack_data))

    local url = "http://127.0.0.1:3000/trigger"
    log("[Damage Trigger] Sending HTTP GET request to: " .. url)

    dohttpreq(url, function(response)
        if response then
            log("[Damage Trigger] HTTP GET request successful. Response: " .. response)
        else
            log("[Damage Trigger] HTTP GET request failed. No response received.")
        end
    end)
end)
